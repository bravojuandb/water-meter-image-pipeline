import base64
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ConfigDict


IMAGE_PATH = Path("data/sample/sample_03.jpeg")

load_dotenv()

client = OpenAI()


class MeterData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    maker_name: str | None
    meter_model_code: str | None
    meter_serial_number: str | None
    reading_black: str | None
    reading_red: str | None


def encode_image(image_path: Path) -> str:
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")


def extract_meter_data(image_path: Path) -> MeterData:
    image_base64 = encode_image(image_path)

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": """
This image contains a water meter.

Extract exactly these fields:

- maker_name: name of company that fabricated the meter
- meter_model_code: model/type code printed near the serial number, or null
- meter_serial_number: numeric serial number only
- reading_black: black digits in the meter display, preserving leading zeros
- reading_red: red digits in the meter display, preserving leading zeros

Do not combine the model code with the serial number.
If any field is unreadable, return null.
Do not guess.

Return JSON only.
""",
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_base64}",
                    },
                ],
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "meter_data",
                "schema": MeterData.model_json_schema(),
                "strict": True,
            }
        },
    )

    return MeterData.model_validate_json(response.output_text)


if __name__ == "__main__":
    result = extract_meter_data(IMAGE_PATH)
    print(result.model_dump_json(indent=2))
