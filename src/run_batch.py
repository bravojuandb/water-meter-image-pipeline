from pathlib import Path
import time

from src.extract_meter import extract_meter_data
from src.process_batch import find_images, process_images, MeterValues


def extract_meter_values(image_path: Path) -> MeterValues:
    meter_data = extract_meter_data(image_path)
    return meter_data.model_dump()


def main() -> None:
    start = time.perf_counter()
    input_dir = Path("data/raw")
    images = find_images(input_dir)
    after_discovery = time.perf_counter()
    results = list(process_images(images, extract_meter_values))
    after_processing = time.perf_counter()

    print(f"Images: {len(images)}")
    print(f"Discovery: {after_discovery - start:.3f}s")
    print(f"Processing: {after_processing - after_discovery:.3f}s")
    print(f"Total: {after_processing - start:.3f}s")

    for result in results:
        print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    main()
