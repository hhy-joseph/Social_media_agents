"""
Main Instagram Agent class that orchestrates the multi-agent system
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("ig_agent")

class InstagramAgent:
    """
    Main class for Instagram content generation and posting
    """
    
    def __init__(
        self, 
        llm=None,
        output_dir=None, 
        prompts_dir=None,
        templates_dir=None,
        email_user=None,
        email_password=None,
        instagram_username=None,
        instagram_password=None
    ):
        """
        Initialize the Instagram Agent
        
        Args:
            llm: Language model to use for content generation
            output_dir: Directory to save output files
            prompts_dir: Directory containing prompt files
            templates_dir: Directory containing SVG templates
            email_user: Email username for notifications
            email_password: Email password for notifications
            instagram_username: Instagram username for posting
            instagram_password: Instagram password for posting
        """
        # Set up LLM
        self.llm = llm
        
        # Create output directory with datetime structure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        date_folder = datetime.now().strftime("%Y-%m-%d")
        
        if output_dir:
            # If output_dir is provided, create a datetime subdirectory structure
            self.base_output_dir = Path(output_dir)
            self.output_dir = self.base_output_dir / date_folder / timestamp
        else:
            # Otherwise use a default path with timestamp
            self.base_output_dir = Path("output")
            self.output_dir = self.base_output_dir / date_folder / timestamp
            
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set directories
        self.prompts_dir = Path(prompts_dir) if prompts_dir else Path(__file__).parent / "prompts"
        self.templates_dir = Path(templates_dir) if templates_dir else Path(__file__).parent / "static"
        
        # Initialize agents
        from ig_agent.agents.content_agent import ContentAgent
        from ig_agent.agents.image_agent import ImageAgent
        from ig_agent.agents.notification_agent import NotificationAgent
        from ig_agent.agents.instagram_poster import InstagramPoster
        
        # Initialize content agent with history file for duplicate detection
        history_dir = os.path.join(Path(__file__).parent.parent, "data")
        os.makedirs(history_dir, exist_ok=True)
        self.content_agent = ContentAgent(
            llm=self.llm,
            prompt_path=os.path.join(self.prompts_dir, "content_generation.txt"),
            history_file=os.path.join(history_dir, "content_history.json")
        )
        
        self.image_agent = ImageAgent(
            templates_dir=self.templates_dir,
            output_dir=self.output_dir
        )
        
        self.notification_agent = NotificationAgent(
            email_user=email_user,
            email_password=email_password
        )
        
        self.instagram_poster = InstagramPoster(
            username=instagram_username,
            password=instagram_password
        )
        
        # Store results
        self.content_json = None
        self.image_paths = []
        self.notification_status = None
        self.instagram_status = None
    
    def generate_content(self, request: str) -> Dict[str, Any]:
        """
        Generate Instagram content based on request
        
        Args:
            request: User request for content generation
            
        Returns:
            Content JSON
        """
        logger.info(f"Generating content for request: {request}")
        self.content_json = self.content_agent.generate(request)
        
        # Ensure content_json is a dictionary
        if isinstance(self.content_json, str):
            try:
                import json
                self.content_json = json.loads(self.content_json)
                logger.info("Successfully parsed string response into JSON")
            except json.JSONDecodeError:
                logger.error("Failed to parse content_json string into JSON")
                raise ValueError("Content agent returned a string that is not valid JSON")
                
        return self.content_json
    
    def generate_images(self, content_json=None) -> List[Dict[str, Any]]:
        """
        Generate images from content
        
        Args:
            content_json: Optional content JSON to use instead of stored content
            
        Returns:
            List of image metadata
        """
        # Use provided content_json or fall back to stored content
        content_to_use = content_json or self.content_json
        
        if not content_to_use:
            raise ValueError("Content must be generated first")
        
        logger.info("Generating images from content")
        images = self.image_agent.generate_images(content_to_use, self.output_dir)
        
        # Extract paths for convenience
        self.image_paths = [img["path"] for img in images if "path" in img]
        
        return images
    
    def send_notification(self, recipient_email: str) -> Dict[str, Any]:
        """
        Send notification email
        
        Args:
            recipient_email: Email address to send notification to
            
        Returns:
            Notification status
        """
        if not self.content_json:
            raise ValueError("Content must be generated first")
        
        if not self.image_paths:
            raise ValueError("Images must be generated first")
        
        logger.info(f"Sending notification to {recipient_email}")
        self.notification_status = self.notification_agent.send_notification(
            self.content_json,
            self.image_paths,
            recipient_email
        )
        
        return self.notification_status
    
    def post_to_instagram(self, caption: str = None, image_paths: List[str] = None) -> Dict[str, Any]:
        """
        Post content to Instagram
        
        Args:
            caption: Optional caption to use instead of stored content
            image_paths: Optional image paths to use instead of stored paths
            
        Returns:
            Posting status
        """
        # Use provided parameters or fall back to stored content
        caption_to_use = caption if caption is not None else self.content_json["caption"] if self.content_json else None
        paths_to_use = image_paths if image_paths is not None else self.image_paths
        
        if not caption_to_use:
            raise ValueError("Caption must be provided or content must be generated first")
        
        if not paths_to_use:
            raise ValueError("Image paths must be provided or images must be generated first")
        
        # If image_paths is a list of dicts with 'path' keys, extract just the paths
        if paths_to_use and isinstance(paths_to_use[0], dict) and 'path' in paths_to_use[0]:
            paths_to_use = [img['path'] for img in paths_to_use]
        
        logger.info("Posting to Instagram")
        self.instagram_status = self.instagram_poster.post_to_instagram(
            caption_to_use,
            paths_to_use
        )
        
        return self.instagram_status
    
    def run_pipeline(self, request: str, recipient_email: str = None, post_to_instagram: bool = False) -> Dict[str, Any]:
        """
        Run complete pipeline
        
        Args:
            request: User request for content generation
            recipient_email: Email address to send notification to
            post_to_instagram: Whether to post to Instagram
            
        Returns:
            Dict with results from all stages
        """
        # Generate content
        content_json = self.generate_content(request)
        
        # Generate images
        images = self.generate_images(content_json)
        
        results = {
            "content": content_json,
            "images": images,
            "output_dir": str(self.output_dir)
        }
        
        # Send notification if email provided
        if recipient_email:
            notification_status = self.send_notification(recipient_email)
            results["notification"] = notification_status
        
        # Post to Instagram if requested
        if post_to_instagram:
            instagram_status = self.post_to_instagram()
            results["instagram"] = instagram_status
        
        return results