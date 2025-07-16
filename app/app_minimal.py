"""
Minimal application for Instagram content generation workflow

This is a simplified version that works with the existing agent structure
while transitioning to workflow patterns.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ig_agent")


class SimpleInstagramWorkflow:
    """
    Simplified workflow for Instagram content generation
    
    This bridges the existing agent system with workflow patterns
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the workflow
        
        Args:
            output_dir: Base directory for output
        """
        self.base_output_dir = Path(output_dir)
        
        # Try to import required modules
        try:
            from langchain_xai import ChatXAI
            self.llm = ChatXAI(
                model="grok-3-mini",
                api_key=os.getenv("XAI_API_KEY"),
                temperature=0.7
            )
            logger.info("LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            self.llm = None
    
    def _create_output_dir(self) -> str:
        """Create timestamped output directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        date_folder = datetime.now().strftime("%Y-%m-%d")
        
        output_dir = self.base_output_dir / date_folder / timestamp
        os.makedirs(output_dir, exist_ok=True)
        
        return str(output_dir)
    
    def generate_content_only(self, request: str) -> Dict[str, Any]:
        """
        Generate content only (first step of workflow)
        
        Args:
            request: User's content generation request
            
        Returns:
            Dictionary with content and metadata
        """
        if not self.llm:
            return {
                "status": "error",
                "error": "LLM not available. Please check XAI_API_KEY environment variable."
            }
        
        try:
            # Import content agent
            from ig_agent.agents.content_agent import ContentAgent
            
            # Initialize content agent
            content_agent = ContentAgent(llm=self.llm)
            
            # Generate content
            logger.info(f"Generating content for: {request}")
            content_json = content_agent.generate(request)
            
            # Create output directory and save content
            output_dir = self._create_output_dir()
            
            # Save content JSON
            import json
            content_path = os.path.join(output_dir, "content.json")
            with open(content_path, 'w', encoding='utf-8') as f:
                json.dump(content_json, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Content saved to: {content_path}")
            
            return {
                "status": "success",
                "content": content_json,
                "output_dir": output_dir,
                "content_path": content_path
            }
            
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def generate_images(self, content_json: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """
        Generate images from content (second step of workflow)
        
        Args:
            content_json: Content generated from previous step
            output_dir: Directory to save images
            
        Returns:
            Dictionary with image metadata
        """
        try:
            # Import image agent
            from ig_agent.agents.image_agent import ImageAgent
            
            # Initialize image agent
            image_agent = ImageAgent()
            
            # Generate images
            logger.info("Generating images from content")
            images = image_agent.generate_images(content_json, output_dir)
            
            return {
                "status": "success",
                "images": images,
                "image_paths": [img["path"] for img in images if "path" in img]
            }
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def run_complete_workflow(
        self, 
        request: str, 
        recipient_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the complete workflow
        
        Args:
            request: User's content generation request
            recipient_email: Optional email for notifications
            
        Returns:
            Dictionary with all results
        """
        # Step 1: Generate content
        content_result = self.generate_content_only(request)
        
        if content_result["status"] == "error":
            return content_result
        
        # Step 2: Generate images
        image_result = self.generate_images(
            content_result["content"], 
            content_result["output_dir"]
        )
        
        # Step 3: Send notification (if requested and configured)
        notification_result = None
        if recipient_email and os.getenv("EMAIL_USER"):
            try:
                from ig_agent.agents.notification_agent import NotificationAgent
                
                notification_agent = NotificationAgent()
                notification_result = notification_agent.send_notification(
                    content_result["content"],
                    image_result.get("image_paths", []),
                    recipient_email
                )
                logger.info(f"Notification result: {notification_result}")
                
            except Exception as e:
                logger.error(f"Notification failed: {str(e)}")
                notification_result = {"status": "error", "error": str(e)}
        
        # Combine results
        final_result = {
            "status": "success",
            "content": content_result["content"],
            "images": image_result.get("images", []),
            "output_dir": content_result["output_dir"],
            "workflow_steps": {
                "content_generation": content_result["status"],
                "image_generation": image_result["status"],
                "notification": notification_result["status"] if notification_result else "skipped"
            }
        }
        
        if notification_result:
            final_result["notification"] = notification_result
        
        return final_result


def main():
    """Example usage"""
    workflow = SimpleInstagramWorkflow()
    
    request = "Create an Instagram post about the latest AI breakthroughs in 2024"
    
    print(f"Running workflow for: {request}")
    result = workflow.run_complete_workflow(request)
    
    print(f"\nWorkflow Status: {result['status']}")
    
    if result["status"] == "success":
        content = result["content"]
        print(f"Topic: {content.get('cover', {}).get('heading_line1', 'N/A')}")
        print(f"Images: {len(result.get('images', []))}")
        print(f"Output: {result['output_dir']}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()