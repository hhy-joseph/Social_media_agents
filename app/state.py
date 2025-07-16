"""
State management for Instagram content generation workflow
"""

from typing import Dict, Any, List, Optional, TypedDict
from typing_extensions import Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class InstagramWorkflowState(TypedDict):
    """
    State for Instagram content generation workflow
    
    This state tracks the entire workflow from content generation to posting
    """
    
    # Input and configuration
    request: str  # User's content request
    output_dir: str  # Directory to save generated content
    recipient_email: Optional[str]  # Email for notifications
    post_to_instagram: bool  # Whether to post to Instagram
    
    # Workflow stage tracking
    current_stage: str  # current, images, notification, instagram, complete
    
    # Generated content
    content_json: Optional[Dict[str, Any]]  # Generated Instagram content
    images: Optional[List[Dict[str, str]]]  # Generated image metadata
    image_paths: Optional[List[str]]  # Paths to generated images
    
    # Status tracking
    content_status: Optional[str]  # success, error
    image_status: Optional[str]  # success, error
    notification_status: Optional[Dict[str, Any]]  # Notification delivery status
    instagram_status: Optional[Dict[str, Any]]  # Instagram posting status
    
    # Error handling
    errors: Annotated[List[str], add_messages]  # List of errors encountered
    
    # Final results
    results: Optional[Dict[str, Any]]  # Final workflow results


def create_initial_state(
    request: str,
    output_dir: str,
    recipient_email: Optional[str] = None,
    post_to_instagram: bool = False
) -> InstagramWorkflowState:
    """
    Create initial state for the workflow
    
    Args:
        request: User's content generation request
        output_dir: Directory to save generated content
        recipient_email: Optional email for notifications
        post_to_instagram: Whether to post content to Instagram
        
    Returns:
        Initial workflow state
    """
    return InstagramWorkflowState(
        request=request,
        output_dir=output_dir,
        recipient_email=recipient_email,
        post_to_instagram=post_to_instagram,
        current_stage="content",
        content_json=None,
        images=None,
        image_paths=None,
        content_status=None,
        image_status=None,
        notification_status=None,
        instagram_status=None,
        errors=[],
        results=None
    )