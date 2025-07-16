"""
Shared tools and schemas for the Instagram content generation workflow
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, conlist


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