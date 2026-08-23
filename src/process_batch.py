from collections.abc import Callable, Iterable, Iterator
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


MeterValues = dict[str, str | None]
Extractor = Callable[[Path], MeterValues]


def find_images(input_dir: Path) -> list[Path]:
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input directory does not exist: {input_dir}")

    valid_paths: list[Path] = []

    for item in input_dir.rglob("*"):
        if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS:
            valid_paths.append(item)

    return sorted(valid_paths)


def process_images(
    image_paths: Iterable[Path],
    extractor: Extractor,
) -> Iterator[BatchResult]:
    for image_path in image_paths:
        try:
            data = extractor(image_path)
            yield BatchSuccess(
                source_file=str(image_path),
                data=data,
            )
        except Exception as exc:
            yield BatchFailure(
                source_file=str(image_path),
                error=f"{type(exc).__name__}: {exc}",
            )


def write_results(output_path: Path, results: Iterable[BatchResult]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as output_file:
        for result in results:
            output_file.write(result.model_dump_json())
            output_file.write("\n")
            output_file.flush()
