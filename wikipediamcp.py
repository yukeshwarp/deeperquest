import requests
import logging
from fastmcp import FastMCP

mcp = FastMCP(name="Wikipedia Search Tool", host="0.0.0.0", port=8053)


def wikipedia_api_call(wikipedia_url, wiki_params):
    try:
        return requests.get(wikipedia_url, params=wiki_params, timeout=10)
    except Exception as e:
        logging.error(f"Error in wikipedia_api_call: {e}")
        raise

@mcp.tool("wikipedia_search")
def wikipedia_extract(query):
    try:
        wikipedia_url = "https://en.wikipedia.org/w/api.php"
        wiki_params = {
            "action": "query",
            "prop": "extracts",
            "titles": query,
            "format": "json",
            "exintro": True,
            "explaintext": True,
        }
        wiki_response = wikipedia_api_call(wikipedia_url, wiki_params)
        if wiki_response.status_code == 200:
            wiki_data = wiki_response.json()
            pages = wiki_data.get("query", {}).get("pages", {})
            results = []
            for _, page in pages.items():
                extract = page.get("extract")
                if extract:
                    results.append(f"[Wikipedia]\n{extract}")
            return results
        else:
            return [f"Wikipedia Error: {wiki_response.status_code}"]
    except Exception as e:
        logging.error(f"Wikipedia Error: {e}")
        return [f"Wikipedia Error: {str(e)}"]
    
if __name__ == "__main__":
    mcp.run(transport="sse")