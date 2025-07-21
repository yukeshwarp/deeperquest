import requests
import logging
import os
from fastmcp import FastMCP
from dotenv import load_dotenv
import urllib.parse
load_dotenv()

mcp = FastMCP(name="SEC Search Tool", host="0.0.0.0", port=8052)

HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

def sec_api_call(sec_url):
    try:
        return requests.get(sec_url, headers = HEADER, timeout=15)
    except Exception as e:
        logging.error(f"Error in sec_api_call: {e}")
        raise

@mcp.tool("sec_search")
def sec_search(query):
    try:
        sec_url = f"https://www.sec.gov/cgi-bin/browse-edgar?company={urllib.parse.quote(query)}&action=getcompany"
        sec_response = sec_api_call(sec_url, headers=HEADER)
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

if __name__ == "__main__":
    mcp.run(transport="sse")