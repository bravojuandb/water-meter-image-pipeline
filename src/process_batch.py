from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class BatchSuccess(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_file: str
    status: Literal["success"] = "success"
    data: dict[str, str | None]
    error: None = None


class BatchFailure(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_file: str
    status: Literal["failed"] = "failed"
    data: None = None
    error: str


BatchResult = BatchSuccess | BatchFailure


def find_images(input_dir: Path) -> list[Path]:
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input directory does not exist: {input_dir}")

    valid_paths: list[Path] = []

    for item in input_dir.rglob("*"):
        if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS:
            valid_paths.append(item)

    return sorted(valid_paths)
