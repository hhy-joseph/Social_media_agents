"""
Main application for Instagram content generation workflow

This application uses LangGraph workflow patterns instead of the previous agentic system.
"""

import os
import logging
import asyncio
from pathlib import Path
from typing import Optional

from .graph import run_workflow
from .utils import ensure_output_directory, validate_dependencies
from .configuration import get_llm


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ig_agent")


class InstagramContentWorkflow:
    """
    Main workflow class for Instagram content generation
    
    This replaces the previous InstagramAgent with a workflow-based approach
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the workflow
        
        Args:
            output_dir: Base directory for output (will create timestamped subdirs)
        """
        # Validate dependencies
        validate_dependencies()
        
        # Set up output directory
        self.base_output_dir = output_dir or "output"
        
        # Verify LLM is available
        try:
            get_llm()
            logger.info("LLM configuration verified")
        except Exception as e:
            logger.error(f"LLM configuration error: {e}")
            raise
    
    async def generate_content(
        self,
        request: str,
        recipient_email: Optional[str] = None,
        post_to_instagram: bool = False,
        output_dir: Optional[str] = None
    ) -> dict:
        """
        Generate Instagram content using the workflow
        
        Args:
            request: User's content generation request
            recipient_email: Optional email for notifications
            post_to_instagram: Whether to post content to Instagram
            output_dir: Optional specific output directory
            
        Returns:
            Dictionary with workflow results
        """
        # Ensure output directory
        if not output_dir:
            output_dir = ensure_output_directory(self.base_output_dir)
        
        logger.info(f"Starting content generation workflow for: {request}")
        logger.info(f"Output directory: {output_dir}")
        
        try:
            # Run the workflow
            results = await run_workflow(
                request=request,
                output_dir=output_dir,
                recipient_email=recipient_email,
                post_to_instagram=post_to_instagram
            )
            
            logger.info("Workflow completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "output_dir": output_dir
            }
    
    def generate_content_sync(
        self,
        request: str,
        recipient_email: Optional[str] = None,
        post_to_instagram: bool = False,
        output_dir: Optional[str] = None
    ) -> dict:
        """
        Synchronous wrapper for generate_content
        
        Args:
            request: User's content generation request
            recipient_email: Optional email for notifications
            post_to_instagram: Whether to post content to Instagram
            output_dir: Optional specific output directory
            
        Returns:
            Dictionary with workflow results
        """
        return asyncio.run(self.generate_content(
            request=request,
            recipient_email=recipient_email,
            post_to_instagram=post_to_instagram,
            output_dir=output_dir
        ))


async def main():
    """
    Example usage of the workflow
    """
    # Create workflow instance
    workflow = InstagramContentWorkflow()
    
    # Example request
    request = "Find a hot topic right now by websearch if the previous post is not related to latest AI trend."
    # Email notification is disabled by default
    # To enable: set recipient_email = os.getenv("NOTIFICATION_EMAIL")
    recipient_email = None
    
    # Run workflow with Instagram posting enabled
    results = await workflow.generate_content(
        request=request,
        recipient_email=recipient_email,
        post_to_instagram=True
    )
    
    # Print results
    print("\n=== Workflow Results ===")
    if results:
        print(f"Status: {'Success' if 'error' not in results else 'Error'}")
        
        if 'content' in results and results['content']:
            content = results['content']
            print(f"Topic: {content.get('cover', {}).get('heading_line1', 'N/A')}")
            print(f"Hashtag: #{content.get('cover', {}).get('hashtag', 'N/A')}")
            print(f"Content pages: {len(content.get('content_pages', []))}")
        
        if 'images' in results and results['images']:
            print(f"Images generated: {len(results['images'])}")
        else:
            print("Images generated: 0")
        
        if 'output_dir' in results:
            print(f"Output saved to: {results['output_dir']}")
        
        if 'notification' in results:
            notif = results['notification']
            print(f"Notification sent: {notif.get('sent', False)}")
        
        if 'instagram' in results:
            insta = results['instagram']
            print(f"Instagram posted: {insta.get('status') == 'success'}")
        
        if 'errors' in results:
            print(f"Errors: {results['errors']}")
    else:
        print("Status: Error - No results returned")


if __name__ == "__main__":
    asyncio.run(main())