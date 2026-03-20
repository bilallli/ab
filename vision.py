import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


def analyze_image(image_base64: str, media_type: str, question: str) -> str:
    """
    Analyze an image using Groq Vision.
    Extracts all visible text and information from any document or image.
    """
    try:
        prompt = f"""You are a document and image analysis assistant.
Your job is to carefully examine this image and respond to the request.

Request: {question}

If this is a document (form, certificate, ID, letter, receipt, invoice etc):
- Extract ALL visible text and data
- List every field and its value clearly
- Use format: **Field Name:** Value
- Include all numbers, dates, names, addresses

If this is a photo or general image:
- Describe what you see in detail
- List all objects, people, text visible
- Note colors, positions, context

Be thorough and extract everything visible."""

        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            max_tokens=2048,
            temperature=0
        )
        return response.choices[0].message.content

    except Exception as e:
        error = str(e)
        print(f"[Vision Error] {error}")
        if "404" in error:
            return "Vision model not available. Please try again."
        return f"Image analysis error: {error}"
