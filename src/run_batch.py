import json
import csv
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

def export_csv(jsonl_path: Path, csv_path: Path) -> None:

    records_to_export = []

    with jsonl_path.open("r", encoding="utf-8") as jsonl_file:
        for line in jsonl_file:
            record = json.loads(line)
            if record["status"] in ("valid", "invalid"):
                records_to_export.append(record)

    fieldnames = [
        "source_file",
        "status",
        "maker_name",
        "meter_model_code",
        "meter_serial_number",
        "reading_black",
        "reading_red",
    ]

    with csv_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer_tool = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer_tool.writeheader()

        for record in records_to_export:
            data = record["data"]
            row = {
                "source_file": record["source_file"],
                "status": record["status"],
                "maker_name": data.get("maker_name"),
                "meter_model_code": data.get("meter_model_code"),
                "meter_serial_number": data.get("meter_serial_number"),
                "reading_black": data.get("reading_black"),
                "reading_red": data.get("reading_red"),
            }

            writer_tool.writerow(row)






def main() -> None:
    start = time.perf_counter()

    DATA_DIR = Path("data")
    INPUT_DIR = DATA_DIR / "raw"
    OUTPUT_JSON = DATA_DIR / "clean" / "results.jsonl"

    OUTPUT_CSV = DATA_DIR / "clean" / "results.csv"

    files_found = find_images(INPUT_DIR)
    after_discovery = time.perf_counter()

    processed_files = load_processed_files(OUTPUT_JSON)

    files_to_process = filter_unprocessed_images(
        files_found, 
        processed_files
    )

    results = process_images(files_to_process, extract_meter_values)
    write_results(OUTPUT_JSON, results)

    after_processing = time.perf_counter()

    export_csv(OUTPUT_JSON, OUTPUT_CSV )

    print(f"Images: {len(files_found)}")
    print(f"Discovery: {after_discovery - start:.3f}s")
    print(f"Processing: {after_processing - after_discovery:.3f}s")
    print(f"Total: {after_processing - start:.3f}s")


if __name__ == "__main__":
    main()
