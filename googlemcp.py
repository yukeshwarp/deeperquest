import requests
import logging
import os
from fastmcp import FastMCP
from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP(name="Google Search Tool", host="0.0.0.0", port=8051)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

def google_search_api_call(google_search_url, google_params):
    try:
        response = requests.get(google_search_url, params=google_params, timeout=15)
        response.raise_for_status()
        return response
    except Exception as e:
        logging.error(f"Error in google_search_api_call: {e}")
        raise

@mcp.tool("google_search")
def google_search(query):
    google_search_url = "https://www.googleapis.com/customsearch/v1"
    google_params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
        "num": 5,
    }
    try:
        response = google_search_api_call(google_search_url, google_params)
        data = response.json()
        google_urls = []
        formatted_results = []
        for i, item in enumerate(data.get("items", [])):
            formatted_results.append(
                f"[Google Result {i + 1}] {item['title']} - {item['displayLink']}\n{item['snippet']}"
            )
            google_urls.append(item["link"])
        return formatted_results, google_urls
    except Exception as e:
        logging.error(f"Google Search Error: {e}")
        return [f"Google Search Error: {str(e)}"], []


if __name__ == "__main__":
    mcp.run(transport="sse")