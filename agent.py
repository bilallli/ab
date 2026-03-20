import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from tools import run_tool, TOOLS

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.3-70b-versatile"

# SYSTEM_PROMPT = """You are a helpful AI assistant like ChatGPT.
# You have memory of the full conversation — always use context from previous messages.
# You have access to these tools:
# - get_current_time: for date and time questions
# - get_weather: for weather questions  
# - calculate: for any math
# - search_wikipedia: for general knowledge and facts
# - search_google: for news, local places, restaurants, current events, prices

# IMPORTANT RULES:
# - For simple greetings like "hello", "hi", "how are you" — answer directly WITHOUT using any tool
# - For factual or real-time questions — always use search_google or search_wikipedia
# - Never say you lack real-time access — use your tools
# - Give friendly, natural, clear answers
# - Always remember what was said earlier in the conversation"""
SYSTEM_PROMPT = """You are a helpful AI assistant like ChatGPT.
You have memory of the full conversation — always use context from previous messages.
You have access to these tools:
- get_current_time: for date and time questions
- get_weather: for weather questions
- calculate: for any math
- search_wikipedia: for general knowledge and facts
- search_google: for news, local places, restaurants, current events, YouTube videos, links

RESPONSE FORMATTING RULES — always follow these:
- Use **bold** for important terms and headings
- Use numbered lists (1. 2. 3.) for steps or multiple items
- Use bullet points (* item) for features or options
- Always include real clickable links (https://...) when user asks for links, videos, or resources
- When asked for YouTube videos, search Google and include real YouTube URLs like https://youtube.com/watch?v=...
- When asked for websites, always include the full https:// URL
- Keep answers clear, structured and easy to read
- Never say you lack real-time access — use your tools instead
- Always remember what was said earlier in the conversation"""


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

        # ── Agent loop ────────────────────────────────────────
        for step in range(10):
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0,
                max_tokens=1024
            )

            msg = response.choices[0].message

            # ── Final answer (no tool calls) ──────────────────
            if not msg.tool_calls:
                content = msg.content or "I could not find an answer."

                # Detect raw JSON bug and fix it
                stripped = content.strip()
                if stripped.startswith("{") or stripped.startswith("["):
                    try:
                        clean = stripped.replace('\\"', '"')
                        parsed = json.loads(clean)
                        if isinstance(parsed, list):
                            parsed = parsed[0]
                        name = parsed.get("name")
                        args = parsed.get("parameters", {})
                        if name:
                            print(f"[Tool-fallback] {name}({args})")
                            result = run_tool(name, args)
                            messages.append({"role": "assistant", "content": content})
                            messages.append({
                                "role": "user",
                                "content": f"Tool result: {result}\n\nNow give a friendly natural answer."
                            })
                            continue
                    except Exception:
                        pass

                history.append({"role": "user", "content": user_message})
                history.append({"role": "assistant", "content": content})
                return content, history

            # ── Execute tool calls ────────────────────────────
            messages.append(msg)

            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                except Exception:
                    args = {}

                print(f"[Tool] {name}({args})")
                result = run_tool(name, args)
                print(f"[Result] {str(result)[:150]}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

        return "Could not complete the goal.", history

    except Exception as e:
        error = str(e)
        print(f"[Error] {error}")
        if "429" in error or "quota" in error.lower():
            return "Rate limited — please wait 1 minute and try again.", history
        if "tool_use_failed" in error or "Failed to call" in error:
            # Retry without tools for this message
            try:
                simple = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    temperature=0,
                    max_tokens=1024
                )
                answer = simple.choices[0].message.content
                history.append({"role": "user", "content": user_message})
                history.append({"role": "assistant", "content": answer})
                return answer, history
            except Exception as e2:
                return f"Error: {str(e2)}", history
        return f"Error: {error}", history


# For terminal use
def run_agent(user_goal: str) -> str:
    answer, _ = run_agent_with_history(user_goal, [])
    return answer