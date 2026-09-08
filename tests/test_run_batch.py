import json

from src.run_batch import load_processed_files


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
