from openai import OpenAI
# from dotenv import load_dotenv
import os, json, requests

# load env
# load_dotenv()
#โหลด secret API KEY 
def get_secret(name: str, default=None):
    
    try:
        import streamlit as st
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    
    return os.getenv(name, default)

from openai import OpenAI

API_KEY       = get_secret("OPENAI_API_KEY")
MODEL         = get_secret("OPENAI_MODEL", "o4-mini")
SERPER_API_KEY= get_secret("SERPER_API_KEY")

if not API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY")

llm = OpenAI(api_key=API_KEY)
#ใช้จาก .env
# API_KEY = os.getenv("OPENAI_API_KEY")
# MODEL = os.getenv("OPENAI_MODEL", "o4-mini")
# SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# if not API_KEY:
#     raise RuntimeError("Missing OPENAI_API_KEY")

# llm = OpenAI(api_key=API_KEY)

def web_search(query: str, num_results: int = 5) -> dict:
   
    if not SERPER_API_KEY:
        return {"error": "SERPER_API_KEY is missing in .env"}

    try:
        
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": num_results,
        }
        r = requests.post("https://google.serper.dev/search", headers=headers, json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()

        
        organic = data.get("organic", []) or []
        results = []
        for item in organic[:num_results]:
            results.append({
                "title": item.get("title"),
                "url": item.get("link"),
                "snippet": item.get("snippet")
            })

       
        extras = {}
        if data.get("answerBox"):
            extras["answerBox"] = data["answerBox"]
        if data.get("knowledgeGraph"):
            kg = data["knowledgeGraph"]
            extras["knowledgeGraph"] = {
                "title": kg.get("title"),
                "type": kg.get("type"),
                "description": kg.get("description")
            }

        out = {"results": results}
        if extras:
            out["extras"] = extras
        return out

    except requests.RequestException as e:
        return {"error": f"serper request failed: {e}"}
    except Exception as e:
        return {"error": f"unexpected error: {e}"}

webSearchTool = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web (Google via Serper) and return top results (title, url, snippet).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "num_results": {"type": "number"},
            },
            "required": ["query"]
        }
    }
}

def chat_with_llm(messages):
    
    resp = llm.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=[webSearchTool],
    )
    return resp



