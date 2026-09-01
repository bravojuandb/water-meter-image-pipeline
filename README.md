# Water Meter Image Pipeline

Extract structured meter data from water meter images with the OpenAI API.

Output consists of the extracted water meter data and a status of `valid`,
`invalid`, or `failed`.

Example output for one image:

```txt
Images: 1
Discovery: 0.001s
Processing: 49.731s
Total: 49.731s
{
  "source_file": "data/raw/image_01.jpeg",
  "status": "valid",
  "data": {
    "maker_name": "DIEHL Metering",
    "meter_model_code": "H231/A",
    "meter_serial_number": "2045490",
    "reading_black": "000124",
    "reading_red": "82"
  },
  "error": null
}
```

## Setup specific for macOS users

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

The `data/raw` directory is ignored by Git because meter images may contain
private data. The pipeline supports JPG, JPEG, PNG, and WebP images.

Run the pipeline:

```sh
python3 -m src.run_batch
```

Results are printed to standard output. Each image is classified as `valid`,
`invalid`, or `failed`.
