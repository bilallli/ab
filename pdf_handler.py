import os
import fitz
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.3-70b-versatile"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF. Returns empty if scanned."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = ""
        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            if text.strip():
                full_text += f"\n--- Page {page_num} ---\n{text}"
        doc.close()
        if len(full_text.strip()) > 50:
            if len(full_text) > 12000:
                full_text = full_text[:12000] + "\n\n[Truncated...]"
            return full_text
        return ""
    except Exception as e:
        print(f"[PDF Text Error] {e}")
        return ""


def pdf_to_images(pdf_bytes: bytes) -> list:
    """Convert each PDF page to a high-quality base64 JPEG."""
    images = []
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            mat = fitz.Matrix(2.5, 2.5)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("jpeg")
            img_b64 = base64.b64encode(img_bytes).decode('utf-8')
            images.append(img_b64)
        doc.close()
    except Exception as e:
        print(f"[PDF Image Error] {e}")
    return images


def analyze_scanned_pdf(pdf_bytes: bytes, question: str, filename: str) -> str:
    """
    Use Groq Vision to extract all visible text and data
    from scanned/image-based PDFs page by page.
    """
    try:
        images = pdf_to_images(pdf_bytes)
        if not images:
            return "Could not convert this PDF to images for analysis."

        print(f"[Vision PDF] Processing {len(images)} page(s)...")

        all_results = []

        for i, img_b64 in enumerate(images[:5], 1):
            print(f"[Vision PDF] Analyzing page {i}...")

            prompt = f"""You are a document data extraction assistant.
Your job is to read this document image carefully and extract ALL visible information.

Task: {question}

Instructions:
- Read every single piece of text visible in the image
- Extract all fields, values, numbers, dates, names
- Organize the extracted data in a clear structured format
- Use labels like: Name:, Date:, Number:, Address: etc
- Do NOT skip any visible information
- If you see a form or table, extract all rows and columns
- Report exactly what you see written in the document"""

            response = client.chat.completions.create(
                model=VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_b64}"
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

            result = response.choices[0].message.content
            all_results.append(f"**Page {i} — Extracted Information:**\n\n{result}")

        return "\n\n---\n\n".join(all_results)

    except Exception as e:
        print(f"[Vision PDF Error] {e}")
        return f"Error analyzing PDF: {str(e)}"


def summarize_pdf(text: str, filename: str) -> str:
    """Summarize a text-based PDF."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert document analyzer.
Provide a structured summary with:
**1. Document Type & Topic**
**2. Main Purpose**
**3. Key Information (bullet points)**
**4. Important Details**
**5. Conclusion**
Use **bold** for section headings."""
                },
                {
                    "role": "user",
                    "content": f"Summarize this document '{filename}':\n\n{text}"
                }
            ],
            max_tokens=1024,
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error summarizing: {str(e)}"


def answer_pdf_question(text: str, question: str, filename: str) -> str:
    """Answer a specific question about PDF content."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are analyzing the document '{filename}'.
Answer questions based on the document content provided.
Be precise, extract exact values, names, dates and numbers.
Use **bold** for important extracted information."""
                },
                {
                    "role": "user",
                    "content": f"Document content:\n{text}\n\nQuestion: {question}"
                }
            ],
            max_tokens=1024,
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"