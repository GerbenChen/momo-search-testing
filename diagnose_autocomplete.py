from __future__ import annotations
import json 
from playwright.sync_api import sync_playwright

URL = "https://www.momoshop.com.tw/main/Main.jsp"
KEYWORD = "洗面乳"
SEARCH_INPUT = "[data-testid='header-search-input']"
SUGGESTION_BUTTONS = "div.mu-z-dropdown button"
AUTOCOMPLETE_ENDPOINT = "autocompleteKeywordV3" 

def run_trial(pw, label: str, **launch_kwargs) -> dict: 
    result = {"trial": label, "requests_fired": [], "suggestion_count": None}

    try:
        browser = pw.chromium.launch(**launch_kwargs)
    except Exception as exc:
        result["outcome"] = f"SKIPPED (could not launch: {type(exc).__name__}: {exc})"
        return result  

    try:
        result["browser_version"] = browser.version 
        context = browser.new_context(
            locale="zh-TW", viewport={"width": 1440, "height": 900}
        )
        page = context.new_page()

        def on_request(request):
            if AUTOCOMPLETE_ENDPOINT in request.url:
                try:
                    body = json.loads(request.post_data or "{}")
                except ValueError:
                    body = {}
                result["requests_fired"].append(body.get("keyword"))
        page.on("request", on_request)
        page.goto(URL, wait_until="domcontentloaded")
        search_input = page.locator(SEARCH_INPUT)
        search_input.wait_for(state="visible", timeout=20000)

        search_input.click()
        search_input.fill("")
        search_input.press_sequentially(KEYWORD, delay=50)
        page.wait_for_timeout(6000)

        result["suggestion_count"] = page.locator(SUGGESTION_BUTTONS).count()
        result["input_value"] = search_input.input_value()
        result["outcome"] = (
            "WORKS" if result["requests_fired"] and result["suggestion_count"]
            else "BROKEN" 
        )
    except Exception as exc:
        result["outcome"] = f"ERROR: {type(exc).__name__}: {exc}"
    finally:
        browser.close()

    return result 


def main():  
    trials = [
        ("bundled Chromium, headless=True  (current config.yaml)", {"headless": True}),
        ("bundled Chromium, headless=False", {"headless": False}),
        ("real Chrome,      headless=True", {"headless": True, "channel": "chrome"}),
        ("real Chrome,      headless=False", {"headless": False, "channel": "chrome"}),
    ]

    results = []
    with sync_playwright() as pw:
        for label, kwargs in trials:
            print(f"running: {label} ...", flush=True)
            results.append(run_trial(pw, label, **kwargs))

    print("\n" + "=" * 78)
    print("RESULTS")
    print("=" * 78)
    for r in results:
        print(f"\n{r['trial']}")
        print(f"  outcome            : {r['outcome']}")
        print(f"  browser version    : {r.get('browser_version', '-')}")
        print(f"  autocomplete calls : {r['requests_fired'] or 'NONE FIRED'}")
        print(f"  suggestions in DOM : {r['suggestion_count']}")

    working = [r["trial"] for r in results if r.get("outcome") == "WORKS"]
    print("\n" + "=" * 78)
    if working:
        print("Configurations where autocomplete works:")
        for w in working:
            print(f"  - {w}")
    else: 
        print("Autocomplete did not work in ANY configuration on this machine.")
    print("=" * 78)


if __name__ == "__main__":
    main()
