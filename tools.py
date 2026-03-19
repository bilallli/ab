# import requests
# from datetime import datetime


# def get_current_time() -> str:
#     return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# def get_weather(city: str) -> str:
#     try:
#         url = f"https://wttr.in/{city}?format=3"
#         r = requests.get(url, timeout=5)
#         return r.text.strip()
#     except Exception as e:
#         return f"Error: {str(e)}"


# def calculate(expression: str) -> str:
#     try:
#         allowed = set("0123456789+-*/()., ")
#         if not all(c in allowed for c in expression):
#             return "Error: invalid characters"
#         return str(round(eval(expression), 4))
#     except Exception as e:
#         return f"Error: {str(e)}"

# def search_wikipedia(query: str) -> str:
#     try:
#         # Use the search endpoint first to find the right page
#         search_url = "https://en.wikipedia.org/w/api.php"
#         params = {
#             "action": "query",
#             "list": "search",
#             "srsearch": query,
#             "format": "json",
#             "utf8": 1
#         }
#         r = requests.get(search_url, params=params, timeout=5)
#         results = r.json()["query"]["search"]
        
#         if not results:
#             return f"No Wikipedia results found for: {query}"
        
#         # Get the top result's page title
#         top_title = results[0]["title"]
        
#         # Now fetch the summary
#         summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{top_title.replace(' ', '_')}"
#         r2 = requests.get(summary_url, timeout=5)
#         data = r2.json()
#         extract = data.get("extract", "")
        
#         if extract:
#             return extract[:600]
#         else:
#             return f"Found page '{top_title}' but could not get summary."
#     except Exception as e:
#         return f"Wikipedia error: {str(e)}"


# TOOLS = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_current_time",
#             "description": "Get current date and time",
#             "parameters": {"type": "object", "properties": {}, "required": []},
#         },
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "get_weather",
#             "description": "Get current weather for any city",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "city": {"type": "string", "description": "City name e.g. Lahore"}
#                 },
#                 "required": ["city"],
#             },
#         },
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "calculate",
#             "description": "Evaluate a math expression like 25 * 48",
#             "parameters": {
#                 "type": "object",
#                 "properties": {"expression": {"type": "string"}},
#                 "required": ["expression"],
#             },
#         },
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "search_wikipedia",
#             "description": "Search Wikipedia for information on any topic",
#             "parameters": {
#                 "type": "object",
#                 "properties": {"query": {"type": "string"}},
#                 "required": ["query"],
#             },
#         },
#     },
# ]


# def run_tool(name: str, args: dict) -> str:
#     if name == "get_current_time":
#         return get_current_time()
#     elif name == "get_weather":
#         return get_weather(**args)
#     elif name == "calculate":
#         return calculate(**args)
#     elif name == "search_wikipedia":
#         return search_wikipedia(**args)
#     else:
#         return f"Unknown tool: {name}"
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_weather(city: str) -> str:
    try:
        url = f"https://wttr.in/{city}?format=3"
        r = requests.get(url, timeout=5)
        return r.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"


def calculate(expression: str) -> str:
    try:
        allowed = set('0123456789+-*/()., ')
        if not all(c in allowed for c in expression):
            return "Error: invalid characters"
        return str(round(eval(expression), 4))
    except Exception as e:
        return f"Error: {str(e)}"


def search_wikipedia(query: str) -> str:
    try:
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "utf8": 1
        }
        r = requests.get(search_url, params=params, timeout=5)
        results = r.json()["query"]["search"]
        if not results:
            return f"No Wikipedia results found for: {query}"
        top_title = results[0]["title"]
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{top_title.replace(' ', '_')}"
        r2 = requests.get(summary_url, timeout=5)
        data = r2.json()
        extract = data.get("extract", "")
        return extract[:600] if extract else f"No summary for '{top_title}'."
    except Exception as e:
        return f"Wikipedia error: {str(e)}"


def search_google(query: str) -> str:
    """Search the web using Google Custom Search API."""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")
        if not api_key or not cse_id:
            return "Google API keys not configured."
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cse_id,
            "q": query,
            "num": 5
        }
        r = requests.get(url, params=params, timeout=8)
        data = r.json()
        if "items" not in data:
            return f"No results found for: {query}"
        results = []
        for item in data["items"]:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            results.append(f"- {title}\n  {snippet}\n  Source: {link}")
        return "\n\n".join(results)
    except Exception as e:
        return f"Google search error: {str(e)}"


# ── Tool definitions ───────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get current date and time",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for any city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name e.g. Lahore"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a math expression like 25 * 48",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Search Wikipedia for general knowledge and factual topics",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_google",
            "description": "Search Google for real-time info, local places, news, restaurants, current events, prices, anything not on Wikipedia",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query e.g. 'restaurants on MM Alam Road Lahore'"}
                },
                "required": ["query"]
            }
        }
    }
]


# ── Tool dispatcher ────────────────────────────────────────────

def run_tool(name: str, args: dict) -> str:
    if name == "get_current_time":
        return get_current_time()
    elif name == "get_weather":
        return get_weather(**args)
    elif name == "calculate":
        return calculate(**args)
    elif name == "search_wikipedia":
        return search_wikipedia(**args)
    elif name == "search_google":
        return search_google(**args)
    else:
        return f"Unknown tool: {name}"