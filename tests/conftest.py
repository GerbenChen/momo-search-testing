import logging
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright
from utils.artifact_manager import artifact_manager
from utils.config_reader import load_config
from utils.logger import configure_logging



configure_logging()
logger = logging.getLogger(__name__)

REPORT_DIR = (Path(__file__).resolve().parent.parent/ "reports")
VIDEO_DIR = REPORT_DIR / "videos"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)
HEALTH_CHECK_TIMEOUT = 10000


@pytest.fixture(scope="session")
def playwright_instance():

    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session", autouse=True)
def momo_is_reachable(playwright_instance):

    config = load_config()
    probe = playwright_instance.request.new_context(timeout=HEALTH_CHECK_TIMEOUT)

    status, detail, error = None, "", None
    try:
        response = probe.get(config["base_url"])
        status = response.status
        if not (200 <= status < 400):
            detail = " ".join(response.text()[:200].split())
    except Exception as exc:
        error = exc
    finally:
        probe.dispose()

    if error is not None:
        pytest.skip(
            f"Could not reach momo from this machine, so the whole suite "
            f"was skipped rather than reported as failures. Probe of "
            f"{config['base_url']} raised {type(error).__name__}: {error}"
        )

    if not (200 <= status < 400):
        pytest.skip(
            f"momo's homepage returned HTTP {status}, so this run could not "
            f"reach the site under test -- skipped rather than reported as "
            f"failures. This usually means a network/proxy block or that "
            f"momo is refusing automated traffic, not a bug this suite "
            f"found."
            + (f" Response body: {detail!r}" if detail else "")
        )

    logger.info(f"Site health check passed: {config['base_url']} -> {status}")


@pytest.fixture(scope="session")
def api_context(playwright_instance):

    config = load_config()
    context = playwright_instance.request.new_context(
        extra_http_headers={"Content-Type": "application/json"},
        timeout=config.get("timeout", 30000),
    )
    yield context
    context.dispose()



@pytest.fixture(scope="function")
def page(request, playwright_instance):

    config = load_config()
    browser_cfg = config["browser"]
    debug_cfg = config["debug"]
    headless = browser_cfg["headless"]
    channel = browser_cfg.get("channel") or None
    if request.node.get_closest_marker("headed") and headless:
        logger.info(
            "Test is marked @pytest.mark.headed -- launching headed, "
            "overriding browser.headless from config"
        )
        headless = False
    viewport = browser_cfg.get(
        "viewport",
        {"width": 1440, "height": 900},
    )
    locale = browser_cfg.get("locale", "zh-TW")
    timeout = config.get("timeout", 30000)

    enable_video = debug_cfg.get("video", False)
    enable_trace = debug_cfg.get("trace", True)
   
    logger.info(f"Starting Test: {request.node.name}")
    logger.info(f"Headless Mode: {headless}")
    logger.info(f"Browser Channel: {channel or 'bundled chromium'}")
    logger.info(f"Viewport: {viewport}")

    launch_kwargs = {"headless": headless}
    if channel:
        launch_kwargs["channel"] = channel

    browser = playwright_instance.chromium.launch(**launch_kwargs)

    context_options = {
        "viewport": viewport,
        "locale": locale,
    }

    if enable_video:
        context_options["record_video_dir"] = str(VIDEO_DIR)
        logger.info("Video Recording Enabled")

    context = browser.new_context(**context_options)
    context.set_default_timeout(timeout)

    if enable_trace:
        context.tracing.start(
            screenshots=True,
            snapshots=True,
            sources=True,
        )
        logger.info("Trace Recording Started")

    page = context.new_page()
    yield page

    test_failed = (
        hasattr(request.node, "rep_call")
        and request.node.rep_call.failed
    )

    logger.info(f"Test Failed: {test_failed}")
    status = "failed" if test_failed else "success"
    screenshot_path = artifact_manager.screenshot_path(
        f"{request.node.name}_{status}"
    )

    try:
        page.screenshot(path=screenshot_path, full_page=True)
        logger.info(f"Screenshot Saved ({status.upper()}): {screenshot_path}")
    except Exception as exc:
        logger.error(f"Screenshot Error: {exc}")

    if enable_trace:
        try:
            if test_failed:
                trace_path = artifact_manager.trace_path(request.node.name)
                context.tracing.stop(path=trace_path)
                logger.info(f"Trace Saved: {trace_path}")
            else:
                context.tracing.stop()
                logger.info("Trace Discarded (Test Passed)")
        except Exception as exc:
            logger.error(f"Trace Error: {exc}")

    video = page.video
    context.close()
    if enable_video and video:
        try:
            logger.info(f"Video Saved: {video.path()}")
        except Exception as exc:
            logger.error(f"Video Error: {exc}")

    browser.close()

    logger.info(f"Finished Test: {request.node.name}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):

    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
    