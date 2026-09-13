import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


REPORT_DIR = (Path(__file__).resolve().parent.parent/ "reports")


class ArtifactManager:

    def __init__(self,report_dir: Optional[Path] = None ) -> None:

        self.report_dir = (
            report_dir  
            if report_dir
            else REPORT_DIR
        )

    @staticmethod
    def sanitize_filename(value: str) -> str:

        value = re.sub(r"[^\w\-_.]",  "_",  value)
        value = re.sub(r"_+", "_", value)
        return value.strip("_")

    @staticmethod
    def generate_timestamp() -> str:

        return datetime.now().strftime("%Y%m%d_%H%M%S")

    @staticmethod
    def generate_uuid(length: int = 8) -> str:

        return uuid.uuid4().hex[:length]

    def ensure_directory(self, folder: str) -> Path:

        artifact_dir = (self.report_dir/folder)
        artifact_dir.mkdir(parents=True, exist_ok=True)
        return artifact_dir

    def generate_path(
        self,
        folder: str,
        prefix: str,
        extension: str, 
        *,
        use_timestamp: bool = True,
        use_uuid: bool = False,
        subfolder_by_date: bool = False 
    ) -> str:

        safe_prefix = (
            self.sanitize_filename(prefix)
        )

        artifact_dir = (
            self.ensure_directory(folder)
        )

        if subfolder_by_date:
            date_folder = datetime.now().strftime("%Y%m%d")

            artifact_dir = (artifact_dir/ date_folder)

            artifact_dir.mkdir(parents=True, exist_ok=True)

        file_parts = [safe_prefix]

        if use_timestamp:
            file_parts.append(self.generate_timestamp())

        if use_uuid:
            file_parts.append(self.generate_uuid())

        filename = ("_".join(file_parts) + f".{extension}")

        return str(artifact_dir / filename)

    def screenshot_path(self, test_name: str) -> str:

        return self.generate_path(
            folder="screenshots",
            prefix=test_name,
            extension="png",
            use_timestamp=True,
            use_uuid=False, 
            subfolder_by_date=True 
        )

    def trace_path(self, test_name: str) -> str:

        return self.generate_path(
            folder="traces",
            prefix=test_name,
            extension="zip",
            use_timestamp=True,
            use_uuid=False,
            subfolder_by_date=True
        )

    def video_path(self, test_name: str) -> str:

        return self.generate_path(
            folder="videos",
            prefix=test_name,
            extension="webm",
            use_timestamp=True,
            use_uuid=True, 
            subfolder_by_date=True
        )


artifact_manager = ArtifactManager() 
