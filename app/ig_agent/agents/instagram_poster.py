"""
Instagram posting agent
"""

import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger("ig_agent.instagram_poster")

class InstagramPoster:
    """
    Agent responsible for posting to Instagram
    """
    
    def __init__(self, username=None, password=None):
        """
        Initialize the InstagramPoster
        
        Args:
            username: Instagram username
            password: Instagram password
        """
        self.username = username or os.environ.get("INSTAGRAM_USERNAME")
        self.password = password or os.environ.get("INSTAGRAM_PASSWORD")
        
        # Check if instagrapi is installed
        try:
            import instagrapi
            self.has_instagrapi = True
        except ImportError:
            self.has_instagrapi = False
            logger.warning("instagrapi not installed. Instagram posting will be simulated.")
            logger.warning("Install with: pip install instagrapi")
    
    def post_to_instagram(self, caption: str, image_paths: List[str]) -> Dict[str, Any]:
        """
        Post content to Instagram using instagrapi
        
        Args:
            caption: Post caption
            image_paths: Paths to images to post
            
        Returns:
            Dict with posting status
        """
        if not self.username or not self.password:
            logger.warning("Instagram credentials not provided")
            return {
                "posted": False,
                "error": "Instagram credentials not provided",
                "suggestion": "Provide username and password when initializing InstagramPoster or set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD environment variables"
            }
        
        if not self.has_instagrapi:
            logger.warning("instagrapi not installed, simulating post")
            return {
                "posted": False,
                "simulated": True,
                "caption": caption,
                "num_images": len(image_paths),
                "suggestion": "Install instagrapi with: pip install instagrapi"
            }
        
        try:
            # Import here to avoid dependency if not needed
            from instagrapi import Client
            
            # Check if paths exist
            valid_paths = []
            for path in image_paths:
                if Path(path).exists():
                    valid_paths.append(path)
                else:
                    logger.warning(f"Image not found: {path}")
            
            if not valid_paths:
                raise ValueError("No valid image paths provided")
            
            # Connect to Instagram
            client = Client()
            client.login(self.username, self.password)
            
            # Upload as carousel
            media = client.album_upload(
                valid_paths,
                caption=caption
            )
            
            logger.info(f"Posted to Instagram: {media.pk}")
            return {
                "posted": True,
                "media_id": media.pk,
                "url": f"https://www.instagram.com/p/{media.code}/"
            }
            
        except Exception as e:
            logger.error(f"Failed to post to Instagram: {str(e)}")
            return {
                "posted": False,
                "error": str(e)
            }