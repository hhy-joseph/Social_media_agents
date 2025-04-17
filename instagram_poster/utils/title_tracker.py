import os
import json
from datetime import datetime

class TitleTracker:
    """Tracks and manages previously used content titles to avoid duplication."""
    
    def __init__(self, storage_path="instagram_poster/data/used_titles.json"):
        self.storage_path = storage_path
        self.titles = self._load_titles()
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
    
    def _load_titles(self):
        """
        Load previously used titles from storage.
        
        Returns:
            dict: Dictionary of used titles with timestamps
        """
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"載入標題歷史記錄時出錯: {e}")
            return {}
    
    def _save_titles(self):
        """Save the current titles dictionary to storage."""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.titles, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"儲存標題歷史記錄時出錯: {e}")
    
    def is_title_used(self, title):
        """
        Check if a title has been used before.
        
        Args:
            title (str): The title to check
            
        Returns:
            bool: True if the title has been used, False otherwise
        """
        return title in self.titles
    
    def add_title(self, title, content_type="unknown"):
        """
        Add a title to the used titles list.
        
        Args:
            title (str): The title to add
            content_type (str): Type of content (news, data_science, etc.)
            
        Returns:
            bool: True if added successfully, False if already exists
        """
        if self.is_title_used(title):
            return False
        
        self.titles[title] = {
            "date": datetime.now().isoformat(),
            "content_type": content_type
        }
        
        self._save_titles()
        return True
    
    def get_used_titles(self, content_type=None, limit=10):
        """
        Get a list of previously used titles, optionally filtered by content type.
        
        Args:
            content_type (str, optional): Filter by content type
            limit (int): Maximum number of titles to return
            
        Returns:
            list: List of used titles
        """
        if content_type:
            filtered_titles = [
                title for title, info in self.titles.items() 
                if info.get("content_type") == content_type
            ]
            return filtered_titles[:limit]
        
        return list(self.titles.keys())[:limit]