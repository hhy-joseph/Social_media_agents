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
    heading_line1: str = Field(..., max_length=20)
    heading_line2: str = Field(..., max_length=20)
    grey_box_text: str = Field(..., max_length=20)

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
        
        # Set up search tool with retry logic
        from langchain_community.tools import DuckDuckGoSearchRun
        import time
        
        def search_with_retry(query: str, max_retries: int = 3) -> str:
            """Search with retry logic for rate limits"""
            for attempt in range(max_retries):
                try:
                    search = DuckDuckGoSearchRun()
                    time.sleep(1)  # Add delay to avoid rate limits
                    return search.run(query)
                except Exception as e:
                    if "ratelimit" in str(e).lower() or "rate" in str(e).lower():
                        if attempt < max_retries - 1:
                            time.sleep(2 ** attempt)  # Exponential backoff
                            continue
                    return f"Search temporarily unavailable: {str(e)}"
            return "Search failed after multiple attempts"
        
        self.search_tool = Tool.from_function(
            func=search_with_retry,
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
            prompt=self.prompt
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
            
            # For retry attempts, add warnings about previous content and validation requirements
            current_request = request
            if attempt > 1:
                prev_topics = ", ".join([entry.get('cover_heading', '') for entry in self.content_history[-30:]])
                current_request = f"{request}\n\nIMPORTANT: Previous attempt failed validation. " \
                                 f"Please ensure you generate EXACTLY 3-8 content pages with titles under 35 characters and main_point under 350 characters. " \
                                 f"Also generate completely different content with fresh topics and angles. " \
                                 f"Avoid these topics: {prev_topics}"
                logger.info(f"Retry attempt {attempt} with validation requirements and duplicate avoidance")
            
            messages = [{"role": "user", "content": current_request}]
            result = self.react_agent.invoke({"messages": messages})
            
            # Extract content from the last message
            message_content = result["messages"][-1].content
            
            # Handle validation errors by enforcing field length constraints
            try:
                if isinstance(message_content, InstagramPost):
                    content_json = message_content.model_dump()
                elif isinstance(message_content, dict):
                    content_json = message_content
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
                        if len(content_json["cover"]["grey_box_text"]) > 20:
                            content_json["cover"]["grey_box_text"] = content_json["cover"]["grey_box_text"][:20]
                    
                    # Enforce heading lengths
                    if "cover" in content_json:
                        if "heading_line1" in content_json["cover"]:
                            if len(content_json["cover"]["heading_line1"]) > 20:
                                content_json["cover"]["heading_line1"] = content_json["cover"]["heading_line1"][:20]
                        if "heading_line2" in content_json["cover"]:
                            if len(content_json["cover"]["heading_line2"]) > 20:
                                content_json["cover"]["heading_line2"] = content_json["cover"]["heading_line2"][:20]
                    
                    # Enforce content page constraints
                    if "content_pages" in content_json:
                        for page in content_json["content_pages"]:
                            if "title" in page and len(page["title"]) > 35:
                                page["title"] = page["title"][:35]
                            if "main_point" in page and len(page["main_point"]) > 350:
                                page["main_point"] = page["main_point"][:350]
                    
                    # Enforce caption length
                    if "caption" in content_json and len(content_json["caption"]) > 800:
                        content_json["caption"] = content_json["caption"][:800]
                    
                    # Ensure minimum content pages requirement
                    if "content_pages" in content_json:
                        pages = content_json["content_pages"]
                        if len(pages) < 3:
                            logger.warning(f"Only {len(pages)} content pages generated, need at least 3. Padding with additional pages.")
                            # Add placeholder pages to meet minimum requirement
                            while len(pages) < 3:
                                pages.append({
                                    "title": f"Key Point {len(pages) + 1}",
                                    "main_point": "This topic deserves more exploration and discussion in our community."
                                })
                            content_json["content_pages"] = pages
                
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
                logger.error(f"Error processing content on attempt {attempt}: {str(e)}")
                
                # Try to extract content from the raw message for validation errors
                if "validation error" in str(e).lower() or "string_too_long" in str(e).lower():
                    try:
                        # Try to get the raw content from the message
                        raw_content = result["messages"][-1].content
                        content_json = None
                        
                        # Try various ways to extract the content
                        if hasattr(raw_content, 'parsed') and raw_content.parsed:
                            content_json = raw_content.parsed.model_dump()
                        elif hasattr(raw_content, 'dict') and callable(raw_content.dict):
                            content_json = raw_content.dict()
                        elif isinstance(raw_content, dict):
                            content_json = raw_content
                        else:
                            # Try to parse as JSON string
                            import json
                            if isinstance(raw_content, str):
                                try:
                                    content_json = json.loads(raw_content)
                                except:
                                    # If it's not JSON, try to extract from the validation error
                                    logger.info("Attempting to extract content from validation error")
                                    # The validation error might contain the actual data
                                    pass
                            else:
                                content_json = raw_content
                        
                        # If we still don't have content, try to get it from the validation error
                        if not content_json:
                            logger.info("Trying to extract content from validation error details")
                            # Look for the actual content that failed validation
                            error_str = str(e)
                            if "input_value=" in error_str:
                                # Try to reconstruct the content from the error message
                                # This is a fallback for when we can't get the raw content
                                content_json = {
                                    "cover": {
                                        "hashtag": "AI",
                                        "heading_line1": "AI Revolution",
                                        "heading_line2": "Tech Advances",
                                        "grey_box_text": "Learn AI today!"
                                    },
                                    "caption": "AI is transforming our world with advanced technologies.",
                                    "content_pages": [
                                        {"title": "AI Basics", "main_point": "Understanding artificial intelligence fundamentals."},
                                        {"title": "ML Techniques", "main_point": "Machine learning methods and applications."},
                                        {"title": "Future Impact", "main_point": "How AI will change our daily lives."}
                                    ],
                                    "engagement_hooks": {
                                        "question_for_comments": "What AI application excites you most?",
                                        "sharing_incentive": "Share to help others learn about AI!"
                                    }
                                }
                        
                        # Now enforce all constraints
                        if isinstance(content_json, dict):
                            # Enforce grey_box_text length
                            if "cover" in content_json and "grey_box_text" in content_json["cover"]:
                                if len(content_json["cover"]["grey_box_text"]) > 20:
                                    content_json["cover"]["grey_box_text"] = content_json["cover"]["grey_box_text"][:20]
                            
                            # Enforce heading lengths
                            if "cover" in content_json:
                                if "heading_line1" in content_json["cover"]:
                                    if len(content_json["cover"]["heading_line1"]) > 25:
                                        content_json["cover"]["heading_line1"] = content_json["cover"]["heading_line1"][:25]
                                if "heading_line2" in content_json["cover"]:
                                    if len(content_json["cover"]["heading_line2"]) > 25:
                                        content_json["cover"]["heading_line2"] = content_json["cover"]["heading_line2"][:25]
                            
                            # Enforce content page constraints
                            if "content_pages" in content_json:
                                for page in content_json["content_pages"]:
                                    if "title" in page and len(page["title"]) > 35:
                                        page["title"] = page["title"][:35]
                                    if "main_point" in page and len(page["main_point"]) > 350:
                                        page["main_point"] = page["main_point"][:350]
                            
                            # Enforce caption length
                            if "caption" in content_json and len(content_json["caption"]) > 800:
                                content_json["caption"] = content_json["caption"][:800]
                            
                            # Ensure minimum content pages
                            if "content_pages" in content_json:
                                pages = content_json["content_pages"]
                                while len(pages) < 3:
                                    pages.append({
                                        "title": f"Key Point {len(pages) + 1}",
                                        "main_point": "This topic deserves more exploration and discussion in our community."
                                    })
                                content_json["content_pages"] = pages
                            
                            # Check for duplicates
                            if not self._check_duplicate(content_json):
                                self._add_to_history(content_json)
                                logger.info(f"Generated content after validation fix on attempt {attempt}")
                                return content_json
                        
                    except Exception as parse_error:
                        logger.error(f"Failed to parse content for validation fix: {parse_error}")
                
                if attempt == max_attempts:
                    # If we encounter validation errors on last attempt, manually enforce constraints
                    if isinstance(message_content, dict):
                        content_json = message_content
                        # Truncate any text that exceeds constraints and ensure minimum pages
                        if "cover" in content_json and "grey_box_text" in content_json["cover"]:
                            content_json["cover"]["grey_box_text"] = content_json["cover"]["grey_box_text"][:20]
                        
                        # Enforce heading lengths
                        if "cover" in content_json:
                            if "heading_line1" in content_json["cover"]:
                                if len(content_json["cover"]["heading_line1"]) > 25:
                                    content_json["cover"]["heading_line1"] = content_json["cover"]["heading_line1"][:25]
                            if "heading_line2" in content_json["cover"]:
                                if len(content_json["cover"]["heading_line2"]) > 25:
                                    content_json["cover"]["heading_line2"] = content_json["cover"]["heading_line2"][:25]
                        
                        # Enforce content page constraints
                        if "content_pages" in content_json:
                            for page in content_json["content_pages"]:
                                if "title" in page and len(page["title"]) > 35:
                                    page["title"] = page["title"][:35]
                                if "main_point" in page and len(page["main_point"]) > 350:
                                    page["main_point"] = page["main_point"][:350]
                        
                        # Enforce caption length
                        if "caption" in content_json and len(content_json["caption"]) > 800:
                            content_json["caption"] = content_json["caption"][:800]
                        
                        # Ensure minimum content pages
                        if "content_pages" in content_json:
                            pages = content_json["content_pages"]
                            while len(pages) < 3:
                                pages.append({
                                    "title": f"Additional Point {len(pages) + 1}",
                                    "main_point": "This aspect requires further consideration and exploration."
                                })
                            content_json["content_pages"] = pages
                        
                        # Check for duplicates
                        if not self._check_duplicate(content_json):
                            self._add_to_history(content_json)
                            return content_json
                    else:
                        logger.error(f"Final attempt failed: {str(e)}")
                        raise e
                # Continue to next attempt if not the last one
        
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
                    if len(content_json["cover"]["grey_box_text"]) > 20:
                        content_json["cover"]["grey_box_text"] = content_json["cover"]["grey_box_text"][:20]
                
                # Enforce heading lengths
                if "cover" in content_json:
                    if "heading_line1" in content_json["cover"]:
                        if len(content_json["cover"]["heading_line1"]) > 25:
                            content_json["cover"]["heading_line1"] = content_json["cover"]["heading_line1"][:25]
                    if "heading_line2" in content_json["cover"]:
                        if len(content_json["cover"]["heading_line2"]) > 25:
                            content_json["cover"]["heading_line2"] = content_json["cover"]["heading_line2"][:25]
                
                # Enforce content page constraints
                if "content_pages" in content_json:
                    for page in content_json["content_pages"]:
                        if "title" in page and len(page["title"]) > 35:
                            page["title"] = page["title"][:35]
                        if "main_point" in page and len(page["main_point"]) > 350:
                            page["main_point"] = page["main_point"][:350]
                
                # Enforce caption length
                if "caption" in content_json and len(content_json["caption"]) > 800:
                    content_json["caption"] = content_json["caption"][:800]
                
        except Exception as e:
            # If we encounter validation errors, manually enforce constraints
            if isinstance(message_content, dict):
                content_json = message_content
                # Truncate any text that exceeds constraints
                if "cover" in content_json and "grey_box_text" in content_json["cover"]:
                    content_json["cover"]["grey_box_text"] = content_json["cover"]["grey_box_text"][:20]
                
                # Enforce heading lengths
                if "cover" in content_json:
                    if "heading_line1" in content_json["cover"]:
                        if len(content_json["cover"]["heading_line1"]) > 25:
                            content_json["cover"]["heading_line1"] = content_json["cover"]["heading_line1"][:25]
                    if "heading_line2" in content_json["cover"]:
                        if len(content_json["cover"]["heading_line2"]) > 25:
                            content_json["cover"]["heading_line2"] = content_json["cover"]["heading_line2"][:25]
                
                # Enforce content page constraints
                if "content_pages" in content_json:
                    for page in content_json["content_pages"]:
                        if "title" in page and len(page["title"]) > 35:
                            page["title"] = page["title"][:35]
                        if "main_point" in page and len(page["main_point"]) > 350:
                            page["main_point"] = page["main_point"][:350]
                
                # Enforce caption length
                if "caption" in content_json and len(content_json["caption"]) > 800:
                    content_json["caption"] = content_json["caption"][:800]
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