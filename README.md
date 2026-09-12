# Water Meter Image Pipeline

A Python batch pipeline that uses the OpenAI API to extract water meter data
from images and reduce manual transcription. It saves all results to JSONL,
exports valid and invalid readings to CSV for human review, and skips
previously recorded image paths on subsequent runs.

- Input: `data/raw/` (must be created by the user).
- JSONL output: `data/clean/results.jsonl`.
- CSV output: `data/clean/results.csv`.

JSONL output consists of the extracted water meter data and a status of `valid`,
`invalid`, or `failed`.


## Example output in stdout after processing one image

```txt
Images: 1
Discovery: 0.001s
Processing: 49.731s
Total: 49.731s
```

`Images` counts all discovered images, including previously processed images
that are skipped. It is not the count of newly processed images.

### Result statuses

- `valid`: extraction completed and both `meter_serial_number` and
  `reading_black` are non-empty.
- `invalid`: extraction completed, but either required field is empty.
- `failed`: extraction raised an error while reading the image, calling the API,
  or parsing the response.

Field-format and numerical validation are deliberately out of scope.


## Setup specific for macOS users

Run all setup and pipeline commands from the repository root so relative paths
resolve correctly.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Add your OpenAI API key to `.env`:

```env
OPENAI_API_KEY=your_api_key
```

The `.env` file is ignored by Git and must not be committed.

## Run

Create the input directory and add the water meter images:

```sh
mkdir -p data/raw
```

The `data/raw` directory is ignored by Git. The pipeline supports JPG, JPEG, PNG, and WebP images.

Run the pipeline:

```sh
python3 -m src.run_batch
```

All results are saved to `data/clean/results.jsonl`, one JSON record per line.
Each record has separate `status` and `data` fields. The status is `valid`,
`invalid`, or `failed`; failed records have `data: null` and an error message.

`data/clean/results.csv` contains only valid and invalid records, including their
source paths, statuses, and extracted data. The CSV is overwritten on every run
using the entire JSONL history.

On subsequent runs, images whose source paths are already recorded in JSONL are
skipped, including previously invalid and failed results. Only images with
unrecorded source paths are sent to the API. Their results are appended to JSONL;
existing records are left unchanged. This check compares paths, not image contents.
