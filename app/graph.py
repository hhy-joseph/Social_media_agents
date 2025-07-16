"""
LangGraph workflow for Instagram content generation

This module implements a sequential workflow using LangGraph standard practices,
moving away from the agentic supervisor pattern to a more straightforward workflow.
"""

import os
import logging
from typing import Literal
from pathlib import Path

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from .state import InstagramWorkflowState, create_initial_state
from .tools_and_schemas import InstagramPost
from .utils import save_content_json

logger = logging.getLogger("ig_agent.graph")


def should_continue_to_images(state: InstagramWorkflowState) -> Literal["generate_images", "handle_error"]:
    """
    Determine if workflow should continue to image generation
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node to execute
    """
    logger.info(f"Checking if should continue to images: content_status={state['content_status']}, has_content={bool(state['content_json'])}")
    if state["content_status"] == "success" and state["content_json"]:
        logger.info("Continuing to image generation")
        return "generate_images"
    else:
        logger.info("Handling error - skipping image generation")
        return "handle_error"


def should_continue_to_notification(state: InstagramWorkflowState) -> Literal["send_notification", "post_instagram", "complete_workflow"]:
    """
    Determine if workflow should continue to notification
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node to execute
    """
    if state["image_status"] == "success":
        if state["recipient_email"]:
            return "send_notification"
        elif state["post_to_instagram"]:
            return "post_instagram"
        else:
            return "complete_workflow"
    else:
        return "complete_workflow"  # Complete with partial results


def should_continue_to_instagram(state: InstagramWorkflowState) -> Literal["post_instagram", "complete_workflow"]:
    """
    Determine if workflow should continue to Instagram posting
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node to execute
    """
    if state["post_to_instagram"]:
        return "post_instagram"
    else:
        return "complete_workflow"


def generate_content_node(state: InstagramWorkflowState) -> Command[Literal["supervisor"]]:
    """
    Generate Instagram content
    
    Args:
        state: Current workflow state
        
    Returns:
        Command with updated state
    """
    try:
        logger.info(f"Generating content for request: {state['request']}")
        
        # Import here to avoid circular imports
        from .ig_agent.agents.content_agent import ContentAgent
        from .configuration import get_llm, get_prompts_dir
        
        # Initialize content agent
        llm = get_llm()
        prompts_dir = get_prompts_dir()
        
        content_agent = ContentAgent(
            llm=llm,
            prompt_path=os.path.join(prompts_dir, "content_generation.txt")
        )
        
        # Generate content
        content_json = content_agent.generate(state["request"])
        
        # Save content to output directory
        if content_json and state["output_dir"]:
            save_content_json(content_json, state["output_dir"])
        
        return Command(
            update={
                "content_json": content_json,
                "content_status": "success",
                "current_stage": "content"
            },
            goto="supervisor"
        )
        
    except Exception as e:
        error_msg = f"Content generation failed: {str(e)}"
        logger.error(error_msg)
        
        return Command(
            update={
                "content_status": "error",
                "errors": [error_msg]
            },
            goto="supervisor"
        )


def generate_images_node(state: InstagramWorkflowState) -> Command[Literal["supervisor"]]:
    """
    Generate images from content
    
    Args:
        state: Current workflow state
        
    Returns:
        Command with updated state
    """
    try:
        logger.info("Generating images from content")
        
        # Import here to avoid circular imports
        from .ig_agent.agents.image_agent import ImageAgent
        from .configuration import get_templates_dir
        
        if not state["content_json"]:
            raise ValueError("No content available for image generation")
        
        # Initialize image agent
        templates_dir = get_templates_dir()
        image_agent = ImageAgent(
            templates_dir=templates_dir,
            output_dir=state["output_dir"]
        )
        
        # Generate images
        images = image_agent.generate_images(state["content_json"], state["output_dir"])
        image_paths = [img["path"] for img in images if "path" in img]
        
        return Command(
            update={
                "images": images,
                "image_paths": image_paths,
                "image_status": "success",
                "current_stage": "images"
            },
            goto="supervisor"
        )
        
    except Exception as e:
        error_msg = f"Image generation failed: {str(e)}"
        logger.error(error_msg)
        
        return Command(
            update={
                "image_status": "error",
                "errors": [error_msg]
            },
            goto="supervisor"
        )


def send_notification_node(state: InstagramWorkflowState) -> Command[Literal["supervisor"]]:
    """
    Send notification email
    
    Args:
        state: Current workflow state
        
    Returns:
        Command with updated state
    """
    try:
        logger.info(f"Sending notification to {state['recipient_email']}")
        
        # Import here to avoid circular imports
        from .ig_agent.agents.notification_agent import NotificationAgent
        from .configuration import get_email_config
        
        if not state["content_json"]:
            raise ValueError("No content available for notification")
            
        if not state["image_paths"]:
            raise ValueError("No images available for notification")
        
        # Initialize notification agent
        email_user, email_password = get_email_config()
        notification_agent = NotificationAgent(
            email_user=email_user,
            email_password=email_password
        )
        
        # Send notification
        notification_status = notification_agent.send_notification(
            state["content_json"],
            state["image_paths"],
            state["recipient_email"]
        )
        
        return Command(
            update={
                "notification_status": notification_status,
                "current_stage": "notification"
            },
            goto="supervisor"
        )
        
    except Exception as e:
        error_msg = f"Notification failed: {str(e)}"
        logger.error(error_msg)
        
        return Command(
            update={
                "notification_status": {"status": "error", "message": error_msg},
                "errors": [error_msg]
            },
            goto="supervisor"
        )


def post_instagram_node(state: InstagramWorkflowState) -> Command[Literal["supervisor"]]:
    """
    Post content to Instagram
    
    Args:
        state: Current workflow state
        
    Returns:
        Command with updated state
    """
    try:
        logger.info("Posting content to Instagram")
        
        # Import here to avoid circular imports
        from .ig_agent.agents.instagram_poster import InstagramPoster
        from .configuration import get_instagram_config
        
        if not state["content_json"]:
            raise ValueError("No content available for Instagram posting")
            
        if not state["image_paths"]:
            raise ValueError("No images available for Instagram posting")
        
        # Initialize Instagram poster
        instagram_username, instagram_password = get_instagram_config()
        instagram_poster = InstagramPoster(
            username=instagram_username,
            password=instagram_password
        )
        
        # Post to Instagram
        caption = state["content_json"].get("caption", "")
        instagram_status = instagram_poster.post_to_instagram(
            caption,
            state["image_paths"]
        )
        
        return Command(
            update={
                "instagram_status": instagram_status,
                "current_stage": "instagram"
            },
            goto="supervisor"
        )
        
    except Exception as e:
        error_msg = f"Instagram posting failed: {str(e)}"
        logger.error(error_msg)
        
        return Command(
            update={
                "instagram_status": {"status": "error", "message": error_msg},
                "errors": [error_msg],
                "current_stage": "instagram"
            },
            goto="supervisor"
        )


def complete_workflow_node(state: InstagramWorkflowState) -> Command[Literal["__end__"]]:
    """
    Complete the workflow and prepare final results
    
    Args:
        state: Current workflow state
        
    Returns:
        Command to end workflow
    """
    logger.info("Completing workflow")
    
    # Prepare final results
    results = {
        "content": state["content_json"],
        "images": state["images"],
        "image_paths": state["image_paths"],
        "output_dir": state["output_dir"]
    }
    
    # Add optional results
    if state["notification_status"]:
        results["notification"] = state["notification_status"]
        
    if state["instagram_status"]:
        results["instagram"] = state["instagram_status"]
        
    if state["errors"]:
        results["errors"] = state["errors"]
    
    return Command(
        update={
            "results": results,
            "current_stage": "complete"
        },
        goto=END
    )


def handle_error_node(state: InstagramWorkflowState) -> Command[Literal["__end__"]]:
    """
    Handle workflow errors
    
    Args:
        state: Current workflow state
        
    Returns:
        Command to end workflow with error
    """
    logger.error("Workflow failed due to errors")
    
    results = {
        "status": "error",
        "errors": state["errors"],
        "output_dir": state["output_dir"]
    }
    
    return Command(
        update={
            "results": results,
            "current_stage": "error"
        },
        goto=END
    )


def supervisor_node(state: InstagramWorkflowState) -> Command[Literal[
    "generate_images", "send_notification", "post_instagram", 
    "complete_workflow", "handle_error"
]]:
    """
    Supervisor node to route workflow based on current stage
    
    Args:
        state: Current workflow state
        
    Returns:
        Command to route to next node
    """
    current_stage = state["current_stage"]
    logger.info(f"Supervisor routing: current_stage={current_stage}")
    
    if current_stage == "content":
        next_node = should_continue_to_images(state)
        logger.info(f"From content stage, routing to: {next_node}")
        return Command(goto=next_node)
    elif current_stage == "images":
        next_node = should_continue_to_notification(state)
        logger.info(f"From images stage, routing to: {next_node}")
        return Command(goto=next_node)
    elif current_stage == "notification":
        next_node = should_continue_to_instagram(state)
        logger.info(f"From notification stage, routing to: {next_node}")
        return Command(goto=next_node)
    elif current_stage == "instagram":
        logger.info("From instagram stage, completing workflow")
        return Command(goto="complete_workflow")
    else:
        logger.info(f"Unknown stage {current_stage}, completing workflow")
        return Command(goto="complete_workflow")


def create_workflow() -> StateGraph:
    """
    Create the Instagram content generation workflow
    
    Returns:
        Compiled LangGraph workflow
    """
    # Create workflow graph
    workflow = StateGraph(InstagramWorkflowState)
    
    # Add nodes
    workflow.add_node("generate_content", generate_content_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("generate_images", generate_images_node)
    workflow.add_node("send_notification", send_notification_node)
    workflow.add_node("post_instagram", post_instagram_node)
    workflow.add_node("complete_workflow", complete_workflow_node)
    workflow.add_node("handle_error", handle_error_node)
    
    # Add edges
    workflow.add_edge(START, "generate_content")
    
    # All nodes route back through supervisor for decision making
    # (except complete_workflow and handle_error which end the workflow)
    
    return workflow.compile()


async def run_workflow(
    request: str,
    output_dir: str,
    recipient_email: str = None,
    post_to_instagram: bool = False
) -> dict:
    """
    Run the complete Instagram content generation workflow
    
    Args:
        request: User's content generation request
        output_dir: Directory to save generated content
        recipient_email: Optional email for notifications
        post_to_instagram: Whether to post content to Instagram
        
    Returns:
        Final workflow results
    """
    # Create initial state
    initial_state = create_initial_state(
        request=request,
        output_dir=output_dir,
        recipient_email=recipient_email,
        post_to_instagram=post_to_instagram
    )
    
    # Create and run workflow
    workflow = create_workflow()
    final_state = await workflow.ainvoke(initial_state)
    
    return final_state["results"]