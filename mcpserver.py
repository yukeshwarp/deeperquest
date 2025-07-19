import urllib.parse
import xml.etree.ElementTree as ET
import logging
from fastmcp import FastMCP
# Import all API call functions from deep_web_agent
from deep_web_agent import (
    google_search_api_call,
    arxiv_api_call,
    sec_api_call,
    wikipedia_api_call,
    newsapi_call,
    google_search,
    arxiv_search,
    newsapi_search,
    sec_search,
    wikipedia_extract,
)

mcp = FastMCP("Demo 🚀")

def arxiv_api_call(arxiv_url):
    try:
        req = urllib.request.Request(arxiv_url)
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        logging.error(f"Error in arxiv_api_call: {e}")
        raise
    
@mcp.tool("arxiv_search")
def arxiv_search_tool(query):
    return arxiv_search(query)

@mcp.tool("google_search")
def google_search_tool(query):
    return google_search(query)

@mcp.tool("newsapi_search")
def newsapi_search_tool(query):
    return newsapi_search(query)

@mcp.tool("sec_search")
def sec_search_tool(query):
    return sec_search(query)

@mcp.tool("wikipedia_extract")
def wikipedia_extract_tool(query):
    return wikipedia_extract(query)

@mcp.tool("google_search_api_call")
def google_search_api_call_tool(google_search_url, google_params):
    return google_search_api_call(google_search_url, google_params)

@mcp.tool("arxiv_api_call")
def arxiv_api_call_tool(arxiv_url):
    return arxiv_api_call(arxiv_url)

@mcp.tool("sec_api_call")
def sec_api_call_tool(sec_url):
    return sec_api_call(sec_url)

@mcp.tool("wikipedia_api_call")
def wikipedia_api_call_tool(wikipedia_url, wiki_params):
    return wikipedia_api_call(wikipedia_url, wiki_params)

@mcp.tool("newsapi_call")
def newsapi_call_tool(newsapi, query):
    return newsapi_call(newsapi, query)

if __name__ == "__main__":
    mcp.run()