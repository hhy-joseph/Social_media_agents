"""
Instagram Agent - A workflow-based system for Instagram content generation
"""

__version__ = "0.2.0"

# Agent classes for workflow nodes
from ig_agent.agents.content_agent import ContentAgent
from ig_agent.agents.image_agent import ImageAgent
from ig_agent.agents.notification_agent import NotificationAgent
from ig_agent.agents.instagram_poster import InstagramPoster