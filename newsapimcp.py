from newsapi import NewsApiClient
import logging
import os
from fastmcp import FastMCP
from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP(name="NewsAPI Search Tool", host="0.0.0.0",port=8050)

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def newsapi_call(newsapi, query):
    try:
        return newsapi.get_everything(
            q=query, language="en", sort_by="relevancy", page_size=5
        )
    except Exception as e:
        logging.error(f"Error in newsapi_call: {e}")
        raise

@mcp.tool("newsapi_search")
def newsapi_search(query):
    try:
        newsapi = NewsApiClient(api_key=NEWSAPI_KEY)
        articles = newsapi_call(newsapi, query)
        results = []
        for i, article in enumerate(articles.get("articles", [])):
            results.append(
                f"[News {i + 1}] {article['title']} ({article['source']['name']})\n{article['description']}\nURL: {article['url']}"
            )
        return results
    except Exception as e:
        logging.error(f"NewsAPI Error: {e}")
        return [f"NewsAPI Error: {str(e)}"]
    
if __name__ == "__main__":
    mcp.run(transport="sse")