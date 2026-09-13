import logging
from datetime import datetime
from pathlib import Path


LOG_DIR = (Path(__file__).resolve().parent.parent/ "reports"/ "logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

_configured = False


def configure_logging(level: int = logging.INFO) -> None:
    global _configured 

    if _configured:
        return

    root = logging.getLogger()
    root.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    )

    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"test_{run_timestamp}.log"

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    root.addHandler(file_handler)
    root.addHandler(stream_handler)

    _configured = True 
