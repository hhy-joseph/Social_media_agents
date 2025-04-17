# instagram_poster/agents/instagram_agent.py
import os
import time
from instagrapi import Client

class InstagramAgent:
    """Agent responsible for posting content to Instagram using instagrapi."""
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = None
    
    def login(self):
        """
        Login to Instagram.
        
        Returns:
            dict: Status of the login operation
        """
        try:
            # Create instagrapi client and login
            print(f"正在登入 Instagram 帳號 {self.username}...")
            
            self.client = Client()
            self.client.login(username=self.username, password=self.password)
            
            return {"status": "success", "message": "成功登入 Instagram"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def upload_post(self, image_paths, caption):
        """
        Upload images to Instagram as a carousel post.
        
        Args:
            image_paths (list): Paths to the images to upload
            caption (str): Caption for the Instagram post
            
        Returns:
            dict: Status of the upload operation
        """
        if not image_paths:
            return {"status": "error", "error": "未提供圖片"}
            
        try:
            # First make sure we're logged in
            if self.client is None:
                login_result = self.login()
                if login_result["status"] == "error":
                    return login_result
            
            # Verify that all image files exist
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    return {"status": "error", "error": f"找不到圖片檔案: {img_path}"}
            
            print(f"正在上傳 {len(image_paths)} 張圖片到 Instagram，說明文字: {caption[:50]}...")
            
            # Upload carousel post using instagrapi
            if len(image_paths) == 1:
                # Single image post
                media = self.client.photo_upload(
                    path=image_paths[0],
                    caption=caption
                )
            else:
                # Carousel post
                media = self.client.album_upload(
                    paths=image_paths,
                    caption=caption
                )
            
            return {
                "status": "success", 
                "message": f"成功上傳 {len(image_paths)} 張圖片到 Instagram",
                "media_id": getattr(media, 'id', None),
                "media_code": getattr(media, 'code', None),
                "image_count": len(image_paths),
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}