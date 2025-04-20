"""
Content generation agent for Instagram posts
"""

import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, conlist
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage

class SearchDecision(BaseModel):
    """Model for search decision output"""
    performed_search: bool
    search_keywords: List[str] = Field(default_factory=list)
    search_reason: str

class Cover(BaseModel):
    """Model for cover page content"""
    hashtag: str
    heading_line1: str = Field(..., max_length=25)
    heading_line2: str = Field(..., max_length=25)
    grey_box_text: str = Field(..., max_length=35)

class ContentPage(BaseModel):
    """Model for content page"""
    title: str = Field(..., max_length=35)
    main_point: str = Field(..., max_length=350)

class EngagementHooks(BaseModel):
    """Model for engagement hooks"""
    question_for_comments: str
    sharing_incentive: str

class InstagramPost(BaseModel):
    """Full Instagram post model"""
    search_decision: SearchDecision
    cover: Cover
    caption: str = Field(..., min_length=100, max_length=800)
    content_pages: conlist(ContentPage, min_length=3, max_length=8)
    engagement_hooks: EngagementHooks
    sources: Optional[List[str]] = None

class ContentAgent:
    """ 
    Agent responsible for generating Instagram content
    """
    
    def __init__(self, llm, prompt_path=None):
        """
        Initialize the ContentAgent
        
        Args:
            llm: Language model instance
            prompt_path: Path to content generation prompt
        """
        self.llm = llm
        self.prompt_path = prompt_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "prompts", 
            "content_generation.txt"
        )
        
        # Set up search tool
        from langchain_community.tools import DuckDuckGoSearchRun
        self.search_tool = Tool.from_function(
            func=DuckDuckGoSearchRun().run,
            name="duckduckgo_search",
            description="Search the web for information about AI and data science topics. Use this for finding latest information."
        )
        
        # Load prompt
        with open(self.prompt_path, 'r') as f:
            self.prompt = f.read()
            
        # Create ReAct agent
        from langgraph.prebuilt import create_react_agent
        self.react_agent = create_react_agent(
            llm, 
            tools=[self.search_tool], 
            prompt=self.prompt,
            response_format=InstagramPost
        )
    
    def generate(self, request: str) -> Dict[str, Any]:
        """
        Generate Instagram content based on request
        
        Args:
            request: User request for content generation
            
        Returns:
            Dict containing generated content
        """
        messages = [{"role": "user", "content": request}]
        result = self.react_agent.invoke({"messages": messages})
        
        # Extract content from the last message
        message_content = result["messages"][-1].content
        
        # Handle validation errors by enforcing field length constraints
        try:
            if isinstance(message_content, InstagramPost):
                content_json = message_content.model_dump()
            else:
                content_json = message_content
                
            # Enforce max_length constraints even if model returns longer strings
            if isinstance(content_json, dict):
                # Enforce grey_box_text length
                if "cover" in content_json and "grey_box_text" in content_json["cover"]:
                    if len(content_json["cover"]["grey_box_text"]) > 35:
                        content_json["cover"]["grey_box_text"] = content_json["cover"]["grey_box_text"][:35]
                        
            return content_json
        except Exception as e:
            # If we encounter validation errors, manually enforce constraints
            if isinstance(message_content, dict):
                # Truncate any text that exceeds constraints
                if "cover" in message_content and "grey_box_text" in message_content["cover"]:
                    message_content["cover"]["grey_box_text"] = message_content["cover"]["grey_box_text"][:35]
                
                return message_content
            else:
                raise e
    
    def node_handler(self, state):
        """
        Handler for LangGraph node
        
        Args:
            state: Current graph state
            
        Returns:
            Command to update state and route to next node
        """
        from langgraph.types import Command
        
        result = self.react_agent.invoke(state)    
        message_content = result["messages"][-1].content
        
        try:
            if isinstance(message_content, InstagramPost):
                content_json = message_content.model_dump()
            else:
                content_json = message_content
                
            # Enforce max_length constraints even if model returns longer strings
            if isinstance(content_json, dict):
                # Enforce grey_box_text length
                if "cover" in content_json and "grey_box_text" in content_json["cover"]:
                    if len(content_json["cover"]["grey_box_text"]) > 35:
                        content_json["cover"]["grey_box_text"] = content_json["cover"]["grey_box_text"][:35]
                
        except Exception as e:
            # If we encounter validation errors, manually enforce constraints
            if isinstance(message_content, dict):
                content_json = message_content
                # Truncate any text that exceeds constraints
                if "cover" in content_json and "grey_box_text" in content_json["cover"]:
                    content_json["cover"]["grey_box_text"] = content_json["cover"]["grey_box_text"][:35]
            else:
                raise e
            
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=f"Content generated: Cover with '{content_json.get('cover', {}).get('heading_line1', '')}' "
                                f"and {len(content_json.get('content_pages', []))} content pages.", 
                        name="content_agent"
                    )
                ],
                "content_json": content_json
            },
            goto="supervisor",
        )