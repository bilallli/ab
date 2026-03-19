# # # # import json
# # # # import os
# # # # from openai import OpenAI
# # # # from dotenv import load_dotenv
# # # # from tools import TOOLS, run_tool

# # # # load_dotenv()

# # # # client = OpenAI(
# # # #     api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"
# # # # )

# # # # # MODEL = "llama-3.3-70b-versatile"
# # # # # MODEL = "llama3-groq-70b-8192-tool-use-preview"
# # # # # MODEL = "mixtral-8x7b-32768"
# # # # MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


# # # # SYSTEM_PROMPT = """You are a helpful AI assistant with tools.
# # # # You can check weather, do math, search Wikipedia, and tell the time.
# # # # Always use tools when real data is needed. Be concise and helpful."""


# # # # def run_agent(user_goal: str) -> str:
# # # #     messages = [
# # # #         {"role": "system", "content": SYSTEM_PROMPT},
# # # #         {"role": "user", "content": user_goal},
# # # #     ]

# # # #     print(f"\n[Agent] Thinking...")

# # # #     for step in range(10):
# # # #         response = client.chat.completions.create(
# # # #             model=MODEL, messages=messages, tools=TOOLS, tool_choice="auto"
# # # #         )

# # # #         msg = response.choices[0].message

# # # #         if not msg.tool_calls:
# # # #             return msg.content

# # # #         messages.append(msg)

# # # #         for tool_call in msg.tool_calls:
# # # #             name = tool_call.function.name
# # # #             args = json.loads(tool_call.function.arguments)
# # # #             print(f"[Tool] Using: {name} with {args}")
# # # #             result = run_tool(name, args)
# # # #             print(f"[Result] {result[:100]}")
# # # #             messages.append(
# # # #                 {"role": "tool", "tool_call_id": tool_call.id, "content": result}
# # # #             )

# # # #     return "Could not complete the goal."
# # # import json
# # # import os
# # # from openai import OpenAI
# # # from dotenv import load_dotenv
# # # from tools import TOOLS, run_tool

# # # load_dotenv()

# # # client = OpenAI(
# # #     api_key=os.getenv("GROQ_API_KEY"),
# # #     base_url="https://api.groq.com/openai/v1"
# # # )

# # # # MODEL = "llama3-groq-70b-8192-tool-use-preview"
# # # MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# # # SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools.
# # # You MUST use the provided tools to answer questions. Never return raw JSON.
# # # Always call the appropriate tool and return a natural language answer.

# # # Available tools:
# # # - get_current_time: for date/time questions
# # # - get_weather: for weather questions (requires city name)
# # # - calculate: for math calculations
# # # - search_wikipedia: for any factual/knowledge questions
# # # """

# # # def run_agent(user_goal: str) -> str:
# # #     messages = [
# # #         {"role": "system", "content": SYSTEM_PROMPT},
# # #         {"role": "user", "content": user_goal}
# # #     ]

# # #     for step in range(10):
# # #         response = client.chat.completions.create(
# # #             model=MODEL,
# # #             messages=messages,
# # #             tools=TOOLS,
# # #             tool_choice="auto",
# # #             temperature=0
# # #         )

# # #         msg = response.choices[0].message

# # #         # If the response looks like raw JSON tool call, force tool execution
# # #         if msg.content and not msg.tool_calls:
# # #             content = msg.content.strip()
# # #             # Detect if model returned raw JSON instead of calling tool
# # #             if content.startswith('{"name"') or content.startswith("{'name'"):
# # #                 try:
# # #                     tool_data = json.loads(content)
# # #                     name = tool_data.get("name")
# # #                     args = tool_data.get("parameters", {})
# # #                     result = run_tool(name, args)
# # #                     messages.append({"role": "assistant", "content": content})
# # #                     messages.append({"role": "user", "content": f"Tool result: {result}\n\nNow give me a proper natural language answer based on this result."})
# # #                     continue
# # #                 except:
# # #                     pass
# # #             return msg.content

# # #         if not msg.tool_calls:
# # #             return msg.content or "I could not find an answer."

# # #         messages.append(msg)

# # #         for tool_call in msg.tool_calls:
# # #             name = tool_call.function.name
# # #             args = json.loads(tool_call.function.arguments)
# # #             print(f"[Tool] {name}({args})")
# # #             result = run_tool(name, args)
# # #             print(f"[Result] {result[:120]}")
# # #             messages.append({
# # #                 "role": "tool",
# # #                 "tool_call_id": tool_call.id,
# # #                 "content": result
# # #             })

# # #     return "Could not complete the goal."
# # import json
# # import os
# # from openai import OpenAI
# # from dotenv import load_dotenv
# # from tools import TOOLS, run_tool

# # load_dotenv()

# # client = OpenAI(
# #     api_key=os.getenv("GROQ_API_KEY"),
# #     base_url="https://api.groq.com/openai/v1"
# # )

# # # MODEL = "llama3-groq-70b-8192-tool-use-preview"
# # # MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
# # MODEL = "llama-3.3-70b-versatile"

# # SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools.
# # You have memory of the entire conversation — always use context from previous messages.
# # Use tools to find real-time information. Never return raw JSON.
# # Always give natural, helpful answers in plain English.

# # Available tools:
# # - get_current_time: for date/time questions
# # - get_weather: for weather questions
# # - calculate: for math
# # - search_wikipedia: for general knowledge
# # - search_google: for local places, news, restaurants, current info, anything real-time
# # """

# # def run_agent_with_history(user_message: str, history: list) -> tuple:
# #     """
# #     Run agent with full conversation history for memory.
# #     Returns (answer, updated_history)
# #     """
# #     # Build messages: system + full history + new user message
# #     messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# #     # Add previous conversation (keep last 10 exchanges to avoid token limits)
# #     for msg in history[-20:]:
# #         messages.append(msg)

# #     # Add current user message
# #     messages.append({"role": "user", "content": user_message})

# #     for step in range(10):
# #         response = client.chat.completions.create(
# #             model=MODEL,
# #             messages=messages,
# #             tools=TOOLS,
# #             tool_choice="auto",
# #             temperature=0
# #         )

# #         msg = response.choices[0].message

# #         # Handle raw JSON bug
# #         if msg.content and not msg.tool_calls:
# #             content = msg.content.strip()
# #             if content.startswith('{"name"') or content.startswith("{'name'"):
# #                 try:
# #                     tool_data = json.loads(content)
# #                     name = tool_data.get("name")
# #                     args = tool_data.get("parameters", {})
# #                     result = run_tool(name, args)
# #                     messages.append({"role": "assistant", "content": content})
# #                     messages.append({
# #                         "role": "user",
# #                         "content": f"Tool result: {result}\n\nNow answer naturally based on this."
# #                     })
# #                     continue
# #                 except:
# #                     pass

# #             # Final answer — save to history
# #             final_answer = msg.content or "I could not find an answer."
# #             history.append({"role": "user", "content": user_message})
# #             history.append({"role": "assistant", "content": final_answer})
# #             return final_answer, history

# #         if not msg.tool_calls:
# #             final_answer = msg.content or "I could not find an answer."
# #             history.append({"role": "user", "content": user_message})
# #             history.append({"role": "assistant", "content": final_answer})
# #             return final_answer, history

# #         # Execute tool calls
# #         messages.append(msg)
# #         for tool_call in msg.tool_calls:
# #             name = tool_call.function.name
# #             args = json.loads(tool_call.function.arguments)
# #             print(f"[Tool] {name}({args})")
# #             result = run_tool(name, args)
# #             print(f"[Result] {result[:120]}")
# #             messages.append({
# #                 "role": "tool",
# #                 "tool_call_id": tool_call.id,
# #                 "content": result
# #             })

# #     return "Could not complete the goal.", history


# # # Keep old function for terminal use
# # def run_agent(user_goal: str) -> str:
# #     answer, _ = run_agent_with_history(user_goal, [])
# #     return answer
# import json
# import os
# from openai import OpenAI
# from dotenv import load_dotenv
# from tools import TOOLS, run_tool

# load_dotenv()

# client = OpenAI(
#     api_key=os.getenv("GROQ_API_KEY"),
#     base_url="https://api.groq.com/openai/v1"
# )

# # MODEL = "llama-3.3-70b-versatile"
# MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools.
# You have memory of the entire conversation.
# Use tools to find real-time information. Never return raw JSON.
# Always give natural, helpful answers in plain English.

# Available tools:
# - get_current_time: for date/time questions
# - get_weather: for weather questions  
# - calculate: for math calculations
# - search_wikipedia: for general knowledge and facts
# - search_google: for local places, news, restaurants, current events
# """


# def clean_history(history: list) -> list:
#     """
#     Remove tool-role messages from history.
#     Only keep user and assistant text messages.
#     This prevents tool call conflicts across sessions.
#     """
#     clean = []
#     for msg in history:
#         if msg.get("role") in ["user", "assistant"]:
#             # Only keep if content is a plain string (not a tool call object)
#             if isinstance(msg.get("content"), str) and msg["content"]:
#                 clean.append({
#                     "role": msg["role"],
#                     "content": msg["content"]
#                 })
#     return clean


# def run_agent_with_history(user_message: str, history: list) -> tuple:
#     """
#     Run agent with conversation history for memory.
#     Returns (answer, updated_history)
#     """
#     # Build clean messages — only user/assistant, no tool messages
#     messages = [{"role": "system", "content": SYSTEM_PROMPT}]

#     # Add last 10 clean history messages to avoid token limits
#     clean = clean_history(history)
#     for msg in clean[-10:]:
#         messages.append(msg)

#     # Add current user message
#     messages.append({"role": "user", "content": user_message})

#     for step in range(10):
#         try:
#             response = client.chat.completions.create(
#                 model=MODEL,
#                 messages=messages,
#                 tools=TOOLS,
#                 tool_choice="auto",
#                 temperature=0
#             )
#         except Exception as e:
#             error_msg = str(e)
#             print(f"[API Error] {error_msg}")
#             return f"API Error: {error_msg}", history

#         msg = response.choices[0].message

#         # ── No tool calls = final answer ──────────────────────
#         if not msg.tool_calls:
#             content = msg.content or "I could not find an answer."

#             # Detect raw JSON bug
#             if content.strip().startswith('{') or content.strip().startswith('['):
#                 try:
#                     clean_str = content.strip().replace('\\"', '"')
#                     parsed = json.loads(clean_str)
#                     if isinstance(parsed, list):
#                         parsed = parsed[0]
#                     name = parsed.get("name")
#                     args = parsed.get("parameters", {})
#                     print(f"[Tool-fallback] {name}({args})")
#                     result = run_tool(name, args)
#                     messages.append({"role": "assistant", "content": content})
#                     messages.append({
#                         "role": "user",
#                         "content": f"Tool result: {result}\n\nNow answer naturally."
#                     })
#                     continue
#                 except Exception:
#                     pass

#             # Save only clean text to history
#             history.append({"role": "user", "content": user_message})
#             history.append({"role": "assistant", "content": content})
#             return content, history

#         # ── Execute tool calls ────────────────────────────────
#         # Add assistant message with tool calls to THIS session only
#         messages.append(msg)

#         for tool_call in msg.tool_calls:
#             name = tool_call.function.name
#             try:
#                 args = json.loads(tool_call.function.arguments)
#             except json.JSONDecodeError:
#                 args = {}

#             print(f"[Tool] {name}({args})")
#             result = run_tool(name, args)
#             print(f"[Result] {result[:150]}")

#             # Add tool result to THIS session messages only
#             # NOT saved to history to avoid cross-session conflicts
#             messages.append({
#                 "role": "tool",
#                 "tool_call_id": tool_call.id,
#                 "content": str(result)
#             })

#     return "Could not complete the goal.", history


# # For terminal use
# def run_agent(user_goal: str) -> str:
#     answer, _ = run_agent_with_history(user_goal, [])
#     return answer
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from tools import run_tool

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Try models in order until one works
MODELS_TO_TRY = [
    "gemini-1.5-flash-latest",
    "gemini-2.0-flash-lite",
    "gemini-1.5-pro-latest",
]

GEMINI_TOOLS = [
    genai.protos.Tool(
        function_declarations=[
            genai.protos.FunctionDeclaration(
                name="get_current_time",
                description="Get the current date and time",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={}
                )
            ),
            genai.protos.FunctionDeclaration(
                name="get_weather",
                description="Get current weather for any city in the world",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "city": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="City name e.g. Lahore, Karachi, London"
                        )
                    },
                    required=["city"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="calculate",
                description="Evaluate any math expression",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "expression": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Math expression e.g. 25 * 48 + 100"
                        )
                    },
                    required=["expression"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="search_wikipedia",
                description="Search Wikipedia for general knowledge and facts",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "query": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Search query"
                        )
                    },
                    required=["query"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="search_google",
                description="Search Google for real-time info: news, local places, restaurants, current events, prices, anything recent",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "query": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Search query e.g. restaurants MM Alam Road Lahore"
                        )
                    },
                    required=["query"]
                )
            ),
        ]
    )
]

SYSTEM_PROMPT = """You are a helpful AI assistant like ChatGPT.
You have access to tools for real-time information.
Always use tools when the question needs current data, news, weather, or local info.
Give clear, natural, friendly answers in the same language the user writes in.
Never say you lack real-time access — use your search tools instead.
Remember the full conversation history and use context from previous messages."""


def get_working_model():
    """Try each model until one works."""
    for model_name in MODELS_TO_TRY:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                tools=GEMINI_TOOLS,
                system_instruction=SYSTEM_PROMPT
            )
            print(f"[Model] Using {model_name}")
            return model
        except Exception as e:
            print(f"[Model] {model_name} failed: {e}")
            continue
    return None


def run_agent_with_history(user_message: str, history: list) -> tuple:
    """
    Run Gemini agent with conversation memory.
    Returns (answer, updated_history)
    """
    try:
        # Get a working model
        model = get_working_model()
        if not model:
            return "All AI models are currently unavailable. Please try again later.", history

        # Build Gemini chat history format
        gemini_history = []
        for msg in history[-20:]:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "user":
                gemini_history.append({
                    "role": "user",
                    "parts": [content]
                })
            elif role == "assistant":
                gemini_history.append({
                    "role": "model",
                    "parts": [content]
                })

        # Start chat with history
        chat = model.start_chat(history=gemini_history)

        # Send user message
        response = chat.send_message(user_message)

        # ── Agentic tool call loop ────────────────────────────
        for step in range(10):
            tool_calls = []
            for part in response.parts:
                if hasattr(part, "function_call") and part.function_call.name:
                    tool_calls.append(part.function_call)

            if not tool_calls:
                break

            # Execute all requested tools
            tool_results = []
            for fc in tool_calls:
                name = fc.name
                args = dict(fc.args)
                print(f"[Tool] {name}({args})")
                result = run_tool(name, args)
                print(f"[Result] {str(result)[:150]}")
                tool_results.append(
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=name,
                            response={"result": str(result)}
                        )
                    )
                )

            # Send tool results back to Gemini
            response = chat.send_message(tool_results)

        # Extract final text answer
        final_answer = response.text if hasattr(response, "text") else "I could not find an answer."

        # Save only clean text to history
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": final_answer})

        return final_answer, history

    except Exception as e:
        error = str(e)
        print(f"[Gemini Error] {error}")

        # Handle quota error nicely
        if "429" in error or "quota" in error.lower():
            msg = "I am currently rate limited. Please wait 1 minute and try again, or create a fresh Gemini API key at aistudio.google.com."
            return msg, history

        # Handle model not found
        if "404" in error or "not found" in error.lower():
            msg = "Model not available. Please try again in a moment."
            return msg, history

        return f"Something went wrong: {error}", history


# For terminal use
def run_agent(user_goal: str) -> str:
    answer, _ = run_agent_with_history(user_goal, [])
    return answer
