"""
Content generation agent for Instagram posts
"""

import os
import json
import logging
import hashlib
import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, conlist
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage
from pathlib import Path

logger = logging.getLogger("ig_agent.content_agent")

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
    
    def __init__(self, llm, prompt_path=None, history_file=None):
        """
        Initialize the ContentAgent
        
        Args:
            llm: Language model instance
            prompt_path: Path to content generation prompt
            history_file: Path to content history file for duplicate detection
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
        
        # Set default history file if not provided
        if not history_file:
            history_dir = os.path.join(Path(__file__).parent.parent.parent, "data")
            os.makedirs(history_dir, exist_ok=True)
            self.history_file = os.path.join(history_dir, "content_history.json")
        else:
            self.history_file = history_file
        
        # Initialize or load content history
        self.content_history = self._load_history()
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """
        Load content history from file
        
        Returns:
            List of content history entries
        """
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse history file: {self.history_file}")
                return []
        else:
            return []
    
    def _save_history(self) -> None:
        """
        Save content history to file
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.content_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save content history: {str(e)}")
    
    def _check_duplicate(self, content_json: Dict[str, Any]) -> bool:
        """
        Check if content is a duplicate
        
        Args:
            content_json: Content to check
            
        Returns:
            True if duplicate, False otherwise
        """
        # Create a content signature based on important fields
        content_fields = [
            content_json.get('cover', {}).get('heading_line1', ''),
            content_json.get('cover', {}).get('heading_line2', ''),
            content_json.get('cover', {}).get('hashtag', '')
        ]
        
        # Add the titles of content pages
        for page in content_json.get('content_pages', []):
            content_fields.append(page.get('title', ''))
        
        # Create a hash of the content
        content_signature = hashlib.md5(''.join(content_fields).encode('utf-8')).hexdigest()
        
        # Check if this signature exists in history
        for entry in self.content_history:
            if entry.get('signature') == content_signature:
                return True
        
        return False
    
    def _add_to_history(self, content_json: Dict[str, Any]) -> None:
        """
        Add content to history
        
        Args:
            content_json: Content to add
        """
        # Create a content signature
        content_fields = [
            content_json.get('cover', {}).get('heading_line1', ''),
            content_json.get('cover', {}).get('heading_line2', ''),
            content_json.get('cover', {}).get('hashtag', '')
        ]
        
        # Add the titles of content pages
        for page in content_json.get('content_pages', []):
            content_fields.append(page.get('title', ''))
        
        content_signature = hashlib.md5(''.join(content_fields).encode('utf-8')).hexdigest()
        
        # Add to history
        self.content_history.append({
            'date': datetime.datetime.now().isoformat(),
            'signature': content_signature,
            'cover_heading': content_json.get('cover', {}).get('heading_line1', '') + ' ' + 
                             content_json.get('cover', {}).get('heading_line2', ''),
            'hashtag': content_json.get('cover', {}).get('hashtag', ''),
            'titles': [page.get('title', '') for page in content_json.get('content_pages', [])]
        })
        
        # Limit history to most recent 100 entries
        if len(self.content_history) > 100:
            self.content_history = self.content_history[-100:]
        
        # Save history
        self._save_history()
    
    def generate(self, request: str, max_attempts: int = 3) -> Dict[str, Any]:
        """
        Generate Instagram content based on request
        
        Args:
            request: User request for content generation
            max_attempts: Maximum number of attempts to generate non-duplicate content
            
        Returns:
            Dict containing generated content
        """
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            
            # For retry attempts, add warning about previous content
            current_request = request
            if attempt > 1:
                prev_topics = ", ".join([entry.get('cover_heading', '') for entry in self.content_history[-3:]])
                current_request = f"{request}\n\nIMPORTANT: Previous content was too similar to existing content. " \
                                 f"Please generate completely different content with fresh topics and angles. " \
                                 f"Avoid these topics: {prev_topics}"
                logger.info(f"Retry attempt {attempt} with modified request to avoid duplicates")
            
            messages = [{"role": "user", "content": current_request}]
            result = self.react_agent.invoke({"messages": messages})
            
            # Extract content from the last message
            message_content = result["messages"][-1].content
            
            # Handle validation errors by enforcing field length constraints
            try:
                if isinstance(message_content, InstagramPost):
                    content_json = message_content.model_dump()
                else:
                    # Handle if the content is a string (possibly JSON string)
                    if isinstance(message_content, str):
                        try:
                            import json
                            content_json = json.loads(message_content)
                        except json.JSONDecodeError:
                            content_json = message_content
                            logger.error(f"Error parsing message content as JSON")
                            raise ValueError(f"Content returned as string but could not be parsed as JSON")
                    else:
                        content_json = message_content
                    
                # Enforce max_length constraints even if model returns longer strings
                if isinstance(content_json, dict):
                    # Enforce grey_box_text length
                    if "cover" in content_json and "grey_box_text" in content_json["cover"]:
                        if len(content_json["cover"]["grey_box_text"]) > 35:
                            content_json["cover"]["grey_box_text"] = content_json["cover"]["grey_box_text"][:35]
                
                # Check if content is a duplicate
                if not self._check_duplicate(content_json):
                    # If not duplicate, add to history and return
                    self._add_to_history(content_json)
                    logger.info(f"Generated unique content on attempt {attempt}")
                    return content_json
                else:
                    logger.info(f"Duplicate content detected on attempt {attempt}/{max_attempts}")
                    if attempt == max_attempts:
                        # Last attempt, use it anyway
                        logger.warning(f"Using duplicate content after {max_attempts} failed attempts")
                        self._add_to_history(content_json)
                        return content_json
                
            except Exception as e:
                # If we encounter validation errors, manually enforce constraints
                if isinstance(message_content, dict):
                    content_json = message_content
                    # Truncate any text that exceeds constraints
                    if "cover" in content_json and "grey_box_text" in content_json["cover"]:
                        content_json["cover"]["grey_box_text"] = content_json["cover"]["grey_box_text"][:35]
                    
                    # Check for duplicates
                    if not self._check_duplicate(content_json):
                        self._add_to_history(content_json)
                        return content_json
                else:
                    logger.error(f"Error processing content: {str(e)}")
                    raise e
        
        # If we somehow got here without returning, use the last generated content
        logger.warning("Using last generated content after all attempts")
        return content_json
    
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
                # Handle if the content is a string (possibly JSON string)
                if isinstance(message_content, str):
                    try:
                        import json
                        content_json = json.loads(message_content)
                    except json.JSONDecodeError:
                        content_json = message_content
                        logger.error(f"Error parsing message content as JSON")
                        raise ValueError(f"Content returned as string but could not be parsed as JSON")
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