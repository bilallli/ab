import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.3-70b-versatile"

# Read the document content to provide context
DOCUMENT_PATH = r"c:\Users\amna7\my-ai-agent\dollar-store-business-case.html"
try:
    with open(DOCUMENT_PATH, "r", encoding="utf-8") as file:
        DOCUMENT_CONTENT = file.read()
except FileNotFoundError:
    DOCUMENT_CONTENT = "Document not found."

SYSTEM_PROMPT = f"""You are a specialized AI assistant.
Your ONLY source of knowledge is the following document:

--- DOCUMENT START ---
{DOCUMENT_CONTENT}
--- DOCUMENT END ---

RESPONSE FORMATTING RULES — always follow these:
1. You must ONLY answer questions based on the information provided in the document above.
2. If the user asks a question that cannot be answered using the document, you MUST reply with: "I can only answer questions related to the Value Bazaar business case document." No exceptions.
3. Do not use any outside knowledge or provide general knowledge.
4. Keep answers clear, structured and easy to read.
"""


def run_agent_with_history(user_message: str, history: list) -> tuple:
    """Run agent with conversation memory. Returns (answer, updated_history)"""
    try:
        # Build messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add last 10 conversation turns
        for msg in history[-20:]:
            if msg.get("role") in ["user", "assistant"]:
                if isinstance(msg.get("content"), str):
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0,
            max_tokens=1024
        )

        msg = response.choices[0].message
        content = msg.content or "I could not find an answer."
        
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": content})
        return content, history

    except Exception as e:
        error = str(e)
        print(f"[Error] {error}")
        if "429" in error or "quota" in error.lower():
            return "Rate limited — please wait 1 minute and try again.", history
        return f"Error: {error}", history


# For terminal use
def run_agent(user_goal: str) -> str:
    answer, _ = run_agent_with_history(user_goal, [])
    return answer