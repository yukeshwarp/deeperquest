import requests
import json

MCP_SERVER_URL = "http://127.0.0.1:1352/mcp/"  # Adjust if your MCP server runs on a different port/path

# Create a session and get the session ID
def get_session_id():
    resp = requests.post(MCP_SERVER_URL + "session", headers={"Accept": "application/json"})
    resp.raise_for_status()
    return resp.json()["session_id"]


def call_mcp_tool(tool, args, session_id):
    payload = {
        "jsonrpc": "2.0",
        "method": tool,
        "params": args,
        "id": 1
    }
    headers = {
        "Accept": "application/json, text/event-stream",
        "X-Session-ID": session_id
    }
    response = requests.post(MCP_SERVER_URL, json=payload, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error calling {tool}: {e}\nResponse: {response.text}")
        return None

def main():
    print("Testing MCP tools...")
    session_id = get_session_id()
    # Test queries
    query = "artificial intelligence"
    google_search_url = "https://www.googleapis.com/customsearch/v1"
    google_params = {"key": "demo", "cx": "demo", "q": query, "num": 1}
    arxiv_url = "http://export.arxiv.org/api/query?search_query=all:artificial+intelligence&start=0&max_results=1"
    sec_url = "https://www.sec.gov/cgi-bin/browse-edgar?company=Microsoft&action=getcompany"
    wikipedia_url = "https://en.wikipedia.org/w/api.php"
    wiki_params = {"action": "query", "prop": "extracts", "titles": "Artificial intelligence", "format": "json", "exintro": True, "explaintext": True}

    # Test each tool
    tools_and_args = [
        ("arxiv_search", {"query": query}),
        ("google_search", {"query": query}),
        ("newsapi_search", {"query": query}),
        ("sec_search", {"query": query}),
        ("wikipedia_extract", {"query": query}),
        ("google_search_api_call", {"google_search_url": google_search_url, "google_params": google_params}),
        ("arxiv_api_call", {"arxiv_url": arxiv_url}),
        ("sec_api_call", {"sec_url": sec_url}),
        ("wikipedia_api_call", {"wikipedia_url": wikipedia_url, "wiki_params": wiki_params}),
        # newsapi_call requires a NewsApiClient instance, which can't be serialized; skip in HTTP test
    ]

    for tool, args in tools_and_args:
        print(f"\nCalling tool: {tool}")
        result = call_mcp_tool(tool, args, session_id)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
