import os
import asyncio
from dotenv import load_dotenv
from config import client
import logging
# from deep_web_agent import search_sec_api
import requests
import urllib.parse
from mcp_use import MCPAgent, MCPClient

HEADERS = {    "User-Agent": "secmcp/1.0 (yukeshwarp@docu3c.com)"
}



load_dotenv()

def sec_api_call(sec_url):
    try:
        return requests.get(sec_url, headers=HEADERS, timeout=15)
    except Exception as e:
        logging.error(f"Error in sec_api_call: {e}")
        raise

def sec_search(query):
    try:
        sec_url = f"https://www.sec.gov/cgi-bin/browse-edgar?company={urllib.parse.quote(query)}&action=getcompany"
        sec_response = sec_api_call(sec_url)
        if sec_response.status_code == 200:
            if "No matching companies" in sec_response.text:
                return [f"SEC API: No filings found for '{query}'."]
            else:
                return [f"SEC API: Filings and data retrieved for {query}. Check SEC's website for details."]
        else:
            return [f"SEC API Error: {sec_response.status_code} - Unable to retrieve data from SEC."]
    except Exception as e:
        logging.error(f"SEC API Error: {e}")
        return [f"SEC API Error: {str(e)}"]
    
def search_sec_api(query):
    """Searches SEC and returns relevant filings for a query."""
    sec_results = sec_search(query)
    return "\n\n".join(sec_results)

def execute_step(step, context):
    """Execute a single research step using function calling and web search."""
    exec_prompt = (
        f"You are a helpful research assistant. Please answer the following research question using the available tools and online sources as needed.\n\n"
        f"Research Question: {step}\n\n"
        f"Context: {context}"
    )
    functions = [
        {
            "name": "search_google_api",
            "description": "Searches Google and returns relevant web results for a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for Google.",
                    }
                },
                "required": ["query"],
            },
        },
        {
            "name": "search_arxiv_api",
            "description": "Searches ArXiv and returns relevant results for a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for ArXiv.",
                    }
                },
                "required": ["query"],
            },
        },
        {
            "name": "search_newsapi_api",
            "description": "Searches NewsAPI and returns relevant news articles for a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for NewsAPI.",
                    }
                },
                "required": ["query"],
            },
        },
        {
            "name": "search_sec_api",
            "description": "Searches SEC and returns relevant filings for a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for SEC.",
                    }
                },
                "required": ["query"],
            },
        },
        {
            "name": "search_wikipedia_api",
            "description": "Searches Wikipedia and returns relevant extracts for a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for Wikipedia.",
                    }
                },
                "required": ["query"],
            },
        },
    ]
    messages = [
        {"role": "system", "content": "You are a helpful research assistant."},
        {"role": "user", "content": exec_prompt},
    ]
    response = client.chat.completions.create(
        model="gpt-4.1", messages=messages, functions=functions, function_call="auto"
    )
    msg = response.choices[0].message
    name = getattr(response, 'model', None)
    if name:
        logging.info(f"Execution step used model: {name}")
    import json
    if msg.function_call:
        fn_name = msg.function_call.name
        search_args = json.loads(msg.function_call.arguments)
        # Use MCP for all except SEC
        if fn_name == "search_google_api":
            web_results = mcp_query_source("google", search_args["query"])
        elif fn_name == "search_arxiv_api":
            web_results = mcp_query_source("arxiv", search_args["query"])
        elif fn_name == "search_newsapi_api":
            web_results = mcp_query_source("newsapi", search_args["query"])
        elif fn_name == "search_sec_api":
            web_results = search_sec_api(search_args["query"])
        elif fn_name == "search_wikipedia_api":
            web_results = mcp_query_source("wikipedia", search_args["query"])
        else:
            web_results = "[Function not implemented]"
        messages.append(
            {"role": "function", "name": fn_name, "content": web_results}
        )
        response2 = client.chat.completions.create(model="gpt-4.1", messages=messages)
        return response2.choices[0].message.content
    else:
        return msg.content

# MCP communication layer for sources

def mcp_query_source(source, query):
    """Let the LLM (LangChain) handle reasoning and tool use, with MCP as a tool callable by the agent."""
    # Map source to environment variable name and default URL
    mcp_env_map = {
        "newsapi": ("MCP_NEWSAPI_URL", "http://20.232.217.19:8050/sse"),
        "wikipedia": ("MCP_WIKIPEDIA_URL", "http://172.210.93.168:8053/sse"),
        "arxiv": ("MCP_ARXIV_URL", "http://20.232.76.152:8950/sse"),
        "google": ("MCP_GOOGLE_URL", "http://52.224.133.79:8051/sse"),
    }
    if source not in mcp_env_map:
        return f"[MCP] Source '{source}' not supported."
    env_var, default_url = mcp_env_map[source]
    url = os.getenv(env_var, default_url)
    if not url:
        return f"[MCP] Endpoint URL for '{source}' is not set. Please set {env_var} in your environment."
    payload = {
        "jsonrpc": "2.0",
        "method": f"{source}_search",
        "params": {"query": query},
        "id": 1
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": HEADERS["User-Agent"]
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=20)
        if resp.status_code != 200:
            return f"[MCP] Error: {source} server returned status {resp.status_code}"
        data = resp.json()
        if "error" in data:
            return f"[MCP] Error: {data['error']}"
        return data.get("result", "[MCP] No result returned.")
    except Exception as e:
        logging.error(f"MCP {source} call failed: {e}")
        return f"[MCP] Exception: {str(e)}"
