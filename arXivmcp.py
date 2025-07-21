import urllib.request
import urllib.parse
import logging
import xml.etree.ElementTree as ET
from fastmcp import FastMCP

mcp = FastMCP(name="arxiv Search Tool", host="0.0.0.0",port=8950)


def arxiv_api_call(arxiv_url):
    try:
        req = urllib.request.Request(arxiv_url)
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        logging.error(f"Error in arxiv_api_call: {e}")
        raise

@mcp.tool("arxiv_search")
def arxiv_search(query):
    try:
        encoded_query = urllib.parse.quote(query)
        arxiv_url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results=3"
        xml_data = arxiv_api_call(arxiv_url)
        root = ET.fromstring(xml_data)
        ns = {"arxiv": "http://www.w3.org/2005/Atom"}
        entries = root.findall("arxiv:entry", ns)
        results = []
        for i, entry in enumerate(entries):
            title = entry.find("arxiv:title", ns)
            summary = entry.find("arxiv:summary", ns)
            title_text = title.text.strip() if title is not None else "No title"
            summary_text = (
                summary.text.strip()[:300] + "..."
                if summary is not None
                else "No summary"
            )
            results.append(
                f"[ArXiv Result {i + 1}] {title_text}\nSummary: {summary_text}"
            )
        return results
    except Exception as e:
        logging.error(f"ArXiv Search Error: {e}")
        return [f"ArXiv Search Error: {str(e)}"]
    

if __name__ == "__main__":
    mcp.run(transport="sse")