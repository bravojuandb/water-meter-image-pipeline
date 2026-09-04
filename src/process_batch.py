from collections.abc import Callable, Iterable, Iterator
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
REQUIRED_FIELDS = (
    "meter_serial_number",
    "reading_black",
)


class BatchValid(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_file: str
    status: Literal["valid"] = "valid"
    data: dict[str, str | None]
    error: None = None


class BatchInvalid(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_file: str
    status: Literal["invalid"] = "invalid"
    data: dict[str, str | None]
    missing_fields: list[str]
    error: None = None


class BatchFailure(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_file: str
    status: Literal["failed"] = "failed"
    data: None = None
    error: str


BatchResult = BatchValid | BatchInvalid | BatchFailure


MeterValues = dict[str, str | None]
Extractor = Callable[[Path], MeterValues]


def is_missing(value: str | None) -> bool:
    return value is None or value.strip() == ""


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
            missing_fields = [
                field_name
                for field_name in REQUIRED_FIELDS
                if is_missing(data.get(field_name))
            ]
            if missing_fields:
                yield BatchInvalid(
                    source_file=str(image_path),
                    data=data,
                    missing_fields=missing_fields,
                )
            else:
                yield BatchValid(
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
