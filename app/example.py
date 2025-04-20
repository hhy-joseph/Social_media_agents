#!/usr/bin/env python3
"""
Example usage of Instagram Agent
"""

import os
import logging
from pathlib import Path
from langchain_xai import ChatXAI
from ig_agent import InstagramAgent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("example")

def main():
    """Run example"""
    # Create output directory
    output_dir = Path("example_output")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize LLM
    try:
        llm = ChatXAI(model="grok-3-mini-beta")
        logger.info("Initialized LLM")
    except ImportError:
        logger.error("langchain_xai is required. Install with: pip install langchain_xai")
        return
    
    # Initialize agent
    agent = InstagramAgent(
        llm=llm,
        output_dir=output_dir,
        # Credentials can be provided directly or via environment variables
        email_user=os.environ.get("EMAIL_USER"),
        email_password=os.environ.get("EMAIL_PASSWORD"),
        instagram_username=os.environ.get("INSTAGRAM_USERNAME"),
        instagram_password=os.environ.get("INSTAGRAM_PASSWORD")
    )
    
    # Generate content
    request = "Generate a carousel post about using AI for data visualization in Python"
    logger.info(f"Generating content for request: {request}")
    content_json = agent.generate_content(request)
    logger.info(f"Content generated with {len(content_json.get('content_pages', []))} pages")
    
    # Generate images
    logger.info("Generating images...")
    images = agent.generate_images()
    logger.info(f"Generated {len(images)} images")
    
    # Send notification if credentials are available
    if os.environ.get("EMAIL_USER") and os.environ.get("EMAIL_PASSWORD"):
        notification_email = os.environ.get("NOTIFICATION_EMAIL", "joseph.hohoyin@gmail.com")
        logger.info(f"Sending notification to {notification_email}...")
        notification_status = agent.send_notification(notification_email)
        logger.info(f"Notification sent: {notification_status['sent']}")
    else:
        logger.info("Email credentials not available, skipping notification")
    
    # Post to Instagram if credentials are available
    if os.environ.get("INSTAGRAM_USERNAME") and os.environ.get("INSTAGRAM_PASSWORD"):
        logger.info("Posting to Instagram...")
        instagram_status = agent.post_to_instagram()
        logger.info(f"Posted to Instagram: {instagram_status['posted']}")
    else:
        logger.info("Instagram credentials not available, skipping post")
    
    logger.info(f"Process completed. Output directory: {output_dir}")

if __name__ == "__main__":
    main()