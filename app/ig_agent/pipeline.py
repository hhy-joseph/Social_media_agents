"""
LangGraph pipeline for Instagram content generation
"""

import os
from typing import Literal, Dict, Any, List, Optional
from typing_extensions import TypedDict
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.types import Command

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: str

class State(MessagesState):
    """State for LangGraph pipeline"""
    next: str
    content_json: Dict[str, Any] = None
    images: List[Dict[str, str]] = None
    notification_status: Dict[str, Any] = None
    output_dir: str = None

def create_pipeline(
    llm, 
    output_dir=None, 
    prompts_dir=None, 
    templates_dir=None, 
    email_user=None, 
    email_password=None
):
    """
    Create LangGraph pipeline for Instagram content generation
    
    Args:
        llm: Language model instance
        output_dir: Directory to save output files
        prompts_dir: Directory containing prompt files
        templates_dir: Directory containing SVG templates
        email_user: Email username for notifications
        email_password: Email password for notifications
        
    Returns:
        Compiled LangGraph pipeline
    """
    # Define the team members
    members = ["content_agent", "image_agent", "notification_agent"]
    options = members + ["FINISH"]
    
    # Load supervisor prompt
    supervisor_prompt_path = os.path.join(
        prompts_dir if prompts_dir else os.path.join(os.path.dirname(__file__), "prompts"), 
        "supervisor.txt"
    )
    
    with open(supervisor_prompt_path, 'r') as f:
        system_prompt = f.read()
    
    # Initialize agents
    from ig_agent.agents.content_agent import ContentAgent
    from ig_agent.agents.image_agent import ImageAgent
    from ig_agent.agents.notification_agent import NotificationAgent
    
    content_agent = ContentAgent(
        llm=llm,
        prompt_path=os.path.join(prompts_dir, "content_generation.txt") if prompts_dir else None,
        history_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "content_history.json")
    )
    
    image_agent = ImageAgent(
        templates_dir=templates_dir,
        output_dir=output_dir
    )
    
    notification_agent = NotificationAgent(
        email_user=email_user,
        email_password=email_password
    )
    
    # Define the supervisor node function
    def supervisor_node(state: State) -> Command[Literal[*members, "__end__"]]:
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]
        if goto == "FINISH":
            goto = END

        return Command(goto=goto, update={"next": goto})
    
    # Build the graph
    builder = StateGraph(State)
    builder.add_edge(START, "supervisor")
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("content_agent", content_agent.node_handler)
    builder.add_node("image_agent", image_agent.node_handler)
    builder.add_node("notification_agent", notification_agent.node_handler)
    
    return builder.compile()