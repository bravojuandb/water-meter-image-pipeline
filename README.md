# Water Meter Image Pipeline

Extract structured meter data from water meter images with the OpenAI API.

## Setup

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

```sh
python src/extract_meter.py
```
