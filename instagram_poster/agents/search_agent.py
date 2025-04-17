from langchain_community.tools import DuckDuckGoSearchRun
import os

class SearchAgent:
    """Agent responsible for searching AI news content online."""
    
    def __init__(self):
        self.search = DuckDuckGoSearchRun(backend="news")
    
    def search_news(self, query):
        """
        Search for AI news using DuckDuckGo.
        
        Args:
            query (str): Search query
            
        Returns:
            dict: Search results or error information
        """
        try:
            results = self.search.invoke(query)
            return {"status": "success", "results": results}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_ai_news(self):
        """
        Get trending AI news.
        
        Returns:
            dict: Search results or error information
        """
        # Search specifically for AI news with a variety of relevant terms
        query = "artificial intelligence AI news latest developments machine learning"
        
        print(f"搜尋人工智慧新聞: {query}")
        return self.search_news(query)