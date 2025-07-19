import streamlit as st
from deep_web_agent import search_arxiv_api, search_google_api, search_newsapi_api, search_sec_api, search_wikipedia_api
from dotenv import load_dotenv
from config import client
import logging

load_dotenv()

def execute_step(step, context):
    """Execute a single research step using function calling and web search."""
    exec_prompt = (
        f"You are an autonomous research agent. Execute the following research step:\n\n"
        f"Step: {step}\n\n"
        f"Context so far: {context}\n\n"
        "Include even the most minor details in your response. "
        "Always search over the internet regarding the relevant details and include content from that, use the search_google function."
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
        {"role": "system", "content": "You are a research execution agent."},
        {"role": "user", "content": exec_prompt},
    ]
    response = client.chat.completions.create(
        model="model-router", messages=messages, functions=functions, function_call="auto"
    )
    msg = response.choices[0].message
    name = getattr(response, 'model', None)
    if name:
        logging.info(f"Execution step used model: {name}")
    import json
    if msg.function_call:
        fn_name = msg.function_call.name
        search_args = json.loads(msg.function_call.arguments)
        if fn_name == "search_google_api":
            web_results = search_google_api(search_args["query"])
        elif fn_name == "search_arxiv_api":
            web_results = search_arxiv_api(search_args["query"])
        elif fn_name == "search_newsapi_api":
            web_results = search_newsapi_api(search_args["query"])
        elif fn_name == "search_sec_api":
            web_results = search_sec_api(search_args["query"])
        elif fn_name == "search_wikipedia_api":
            web_results = search_wikipedia_api(search_args["query"])
        else:
            web_results = "[Function not implemented]"
        messages.append(
            {"role": "function", "name": fn_name, "content": web_results}
        )
        response2 = client.chat.completions.create(model="model-router", messages=messages)
        return response2.choices[0].message.content
    else:
        return msg.content

# MCP communication layer for sources

def mcp_query_source(source, query):
    """Communicate with a source (e.g., Google, Arxiv, NewsAPI, SEC, Wikipedia) through MCP."""
    # This is a placeholder for actual MCP integration
    # In a real implementation, you would use the MCP protocol to route the query to the correct source
    # For demonstration, we just call the local function
    if source == "google":
        return search_google_api(query)
    elif source == "arxiv":
        return search_arxiv_api(query)
    elif source == "newsapi":
        return search_newsapi_api(query)
    elif source == "sec":
        return search_sec_api(query)
    elif source == "wikipedia":
        return search_wikipedia_api(query)
    else:
        return f"[MCP] Source '{source}' not supported."
