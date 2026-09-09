import json
import time
from pathlib import Path

from src.process_batch import (
    MeterValues,
    find_images,
    process_images,
    write_results,
)


def extract_meter_values(image_path: Path) -> MeterValues:
    from src.extract_meter import extract_meter_data

    meter_data = extract_meter_data(image_path)
    return meter_data.model_dump()


def load_processed_files(output_path: Path) -> set[str]:
    filenames = set()
    if not output_path.exists():
        return set()

    with output_path.open("r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)
            filenames.add(record["source_file"])

    return filenames

def filter_unprocessed_images(
    image_paths: list[Path],
    processed_files: set[str],
) -> list[Path]:
    files_to_process = []

    for image_path in image_paths:
        if str(image_path) not in processed_files:
            files_to_process.append(image_path)

    return files_to_process

def main() -> None:
    start = time.perf_counter()
    input_dir = Path("data/raw")
    output_path = Path("data/clean/results.jsonl")

    files_found = find_images(input_dir)
    after_discovery = time.perf_counter()

    processed_files = load_processed_files(output_path)

    files_to_process = filter_unprocessed_images(
        files_found, 
        processed_files
    )

    results = process_images(files_to_process, extract_meter_values)
    write_results(output_path, results)

    after_processing = time.perf_counter()

    print(f"Images: {len(files_found)}")
    print(f"Discovery: {after_discovery - start:.3f}s")
    print(f"Processing: {after_processing - after_discovery:.3f}s")
    print(f"Total: {after_processing - start:.3f}s")


if __name__ == "__main__":
    main()
