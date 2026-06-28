import requests
import wikipediaapi
import logging
from config.config import WIKI_USER_AGENT

logger = logging.getLogger(__name__)

class WikiService:
    def __init__(self, user_agent=WIKI_USER_AGENT):
        self.wiki = wikipediaapi.Wikipedia(
            user_agent=user_agent,
            language='en'
        )

    def verify_fact(self, query: str) -> dict:
        """
        Search Wikipedia for the query, retrieve the top article's summary and URL.
        """
        if not query.strip():
            return {
                "success": False,
                "message": "Query cannot be empty."
            }

        try:
            # 1. Search Wikipedia for the closest page title
            search_url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "utf8": 1
            }
            headers = {
                "User-Agent": WIKI_USER_AGENT
            }
            
            response = requests.get(search_url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            search_results = data.get("query", {}).get("search", [])
            if not search_results:
                return {
                    "success": False,
                    "message": f"No Wikipedia articles found for '{query}'."
                }
            
            # Get the top search result title
            top_title = search_results[0]["title"]
            logger.info(f"Top Wikipedia search result for '{query}': {top_title}")
            
            # 2. Fetch the page details using wikipedia-api
            page = self.wiki.page(top_title)
            if not page.exists():
                return {
                    "success": False,
                    "message": f"Article '{top_title}' was found but could not be retrieved."
                }
                
            return {
                "success": True,
                "title": page.title,
                "summary": page.summary[:600] + ("..." if len(page.summary) > 600 else ""),
                "url": page.fullurl
            }

        except requests.exceptions.RequestException as re_err:
            logger.error(f"Network error searching Wikipedia: {re_err}")
            return {
                "success": False,
                "message": "Network error connecting to Wikipedia. Please try again later."
            }
        except Exception as e:
            logger.error(f"Error verifying fact on Wikipedia: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"An error occurred during fact check: {str(e)}"
            }

# Global wiki service instance
wiki_service = WikiService()
