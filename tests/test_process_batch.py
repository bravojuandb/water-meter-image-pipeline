from pathlib import Path

from src.process_batch import BatchInvalid, BatchValid, process_images


def test_complete_required_fields_are_valid():
    image = [Path("fake_image_01.jpg")]

    def fake_extractor(_image_path: Path):
        return {
            "maker_name": None,
            "meter_model_code": None,
            "meter_serial_number": "ABC",
            "reading_black": "001306",
            "reading_red": None,
        }

    results = list(process_images(image, fake_extractor))

    assert len(results) == 1
    assert isinstance(results[0], BatchValid)


def test_missing_serial_number_is_invalid():
    image = [Path("fake_image_02.jpg")]

    def fake_extractor(_image_path: Path):
        return {
            "maker_name": None,
            "meter_model_code": None,
            "meter_serial_number": None,
            "reading_black": "003000",
            "reading_red": None,
        }

    results = list(process_images(image, fake_extractor))

    assert len(results) == 1
    assert isinstance(results[0], BatchInvalid)
    assert results[0].missing_fields == ["meter_serial_number"]
