import base64
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


IMAGE_PATH = Path("data/sample/sample_03.jpeg")

load_dotenv()

client = OpenAI()


def encode_image(image_path: Path) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def extract_meter_data(image_path: Path) -> str:
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
    )

    return response.output_text


if __name__ == "__main__":
    result = extract_meter_data(IMAGE_PATH)
    print(result)