import json
import csv
from pathlib import Path

from src.run_batch import (
    load_processed_files,
    filter_unprocessed_images,
    export_csv,
)


def test_missing_file_returns_empty_set(tmp_path):
    output_path = tmp_path / "results.jsonl"
    filenames = load_processed_files(output_path)

    assert filenames == set()


def test_existing_file_returns_unique_source_files(tmp_path):
    output_path = tmp_path / "results.jsonl"

    records = [
        {"source_file": "file_01", "status": "valid"},
        {"source_file": "file_02", "status": "failed"},
        {"source_file": "file_01", "status": "invalid"},
    ]

    with output_path.open("w", encoding="utf-8") as file:
        for record in records:
            record_json = json.dumps(record)
            file.write(record_json)
            file.write("\n")

    filenames = load_processed_files(output_path)
    assert filenames == {"file_01", "file_02"}


def test_filter_unprocessed_images_skips_processed_files():
    files_found = [Path("A.jpg"), Path("B.jpg"), Path("C.jpg")]
    processed_files = {"B.jpg"}
    result = filter_unprocessed_images(files_found, processed_files)

    assert result == [Path("A.jpg"), Path("C.jpg")]


def test_export_csv_works_with_valid_invalid_and_failed(tmp_path):
    records = [
        {
            "source_file": "file_01",
            "status": "valid",
            "data": {
                "maker_name": "diehl",
                "meter_model_code": "456",
                "meter_serial_number": "123455",
                "reading_black": "000300",
                "reading_red": "50",
            },
            "error": None,
        },
        {
            "source_file": "file_02",
            "status": "invalid",
            "data": {
                "maker_name": "diehl",
                "meter_model_code": "456",
                "meter_serial_number": None,
                "reading_black": "001025",
                "reading_red": None,
            },
            "missing_fields": ["meter_serial_number"],
            "error": None,
        },
        {
            "source_file": "file_03",
            "status": "failed",
            "data": None,
            "error": "TimeoutError: Request timed out",
        },
    ]

    jsonl_path = tmp_path / "results.jsonl"
    csv_path = tmp_path / "results.csv"

    with jsonl_path.open("w", encoding="utf-8") as jsonl_file:
        for record in records:
            jsonl_file.write(json.dumps(record))
            jsonl_file.write("\n")

    export_csv(jsonl_path, csv_path)

    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert rows == [
        {
            "source_file": "file_01",
            "status": "valid",
            "maker_name": "diehl",
            "meter_model_code": "456",
            "meter_serial_number": "123455",
            "reading_black": "000300",
            "reading_red": "50",
        },
        {
            "source_file": "file_02",
            "status": "invalid",
            "maker_name": "diehl",
            "meter_model_code": "456",
            "meter_serial_number": "",
            "reading_black": "001025",
            "reading_red": "",
        },
    ]
