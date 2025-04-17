import os
from typing import Dict, Any
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END

from instagram_poster.agents.date_agent import DateAgent
from instagram_poster.agents.search_agent import SearchAgent
from instagram_poster.agents.content_agent import ContentAgent
from instagram_poster.agents.image_agent import ImageAgent
from instagram_poster.agents.instagram_agent import InstagramAgent
from instagram_poster.config import (
    INSTAGRAM_USERNAME, 
    INSTAGRAM_PASSWORD, 
    MODEL_NAME, 
    COVER_TEMPLATE_PATH,
    CONTENT_TEMPLATE_PATH,
    OUTPUT_DIR
)

# Load environment variables
load_dotenv()

# Initialize agents
date_agent = DateAgent()
search_agent = SearchAgent()
content_agent = ContentAgent(model_name=MODEL_NAME)
image_agent = ImageAgent(
    cover_template_path=COVER_TEMPLATE_PATH,
    content_template_path=CONTENT_TEMPLATE_PATH,
    output_dir=OUTPUT_DIR
)
instagram_agent = InstagramAgent(
    username=INSTAGRAM_USERNAME,
    password=INSTAGRAM_PASSWORD
)

# Define state type for type hinting
class State(Dict[str, Any]):
    """State object for the workflow."""
    pass

def determine_content_type(state: State) -> State:
    """
    Determine the content type based on the current date.
    
    Args:
        state (State): Current workflow state
        
    Returns:
        State: Updated state with content type
    """
    result = date_agent.determine_content_type()
    return {**state, "date_info": result}

def search_ai_news(state: State) -> State:
    """
    Search for AI news.
    
    Args:
        state (State): Current workflow state
        
    Returns:
        State: Updated state with news results
    """
    result = search_agent.get_ai_news()
    return {**state, "news_data": result}

def generate_ai_news_content(state: State) -> State:
    """
    Generate AI news content based on search results.
    
    Args:
        state (State): Current workflow state
        
    Returns:
        State: Updated state with generated content
    """
    news_data = state.get("news_data", {})
    content = content_agent.generate_ai_news_content(news_data)
    
    # Debug print to examine the content structure
    print(f"Content structure: {type(content)}")
    if isinstance(content, dict):
        print(f"Content keys: {content.keys()}")
        print(f"Title: {content.get('title', 'No title found')}")
        print(f"Description: {content.get('description', 'No description found')[:50]}...")
        print(f"Content pages: {len(content.get('content', []))} pages")
    
    return {**state, "content": content}

def generate_images(state: State) -> State:
    """
    Generate SVG files based on content.
    
    Args:
        state (State): Current workflow state
        
    Returns:
        State: Updated state with SVG file paths
    """
    print(f"State keys in generate_images: {state.keys()}")
    
    content = state.get("content", {})
    print(f"Content type: {type(content)}")
    if isinstance(content, dict):
        print(f"Content keys: {content.keys()}")
    else:
        print("Content is not a dictionary")
    
    # Generate SVGs (which will be saved as SVG files, not converted to PNG)
    images = image_agent.generate_images(content)
    
    return {**state, "images": images}

def should_post_to_instagram(state: State) -> str:
    """
    Always return 'skip_instagram' since we're not actually posting to Instagram in this simplified version.
    
    Args:
        state (State): Current workflow state
        
    Returns:
        str: Next node to execute (always 'skip_instagram')
    """
    print("跳過 Instagram 發布，直接生成 SVG 檔案。")
    return "skip_instagram"

def post_to_instagram(state: State) -> State:
    """
    Post content to Instagram (not used in this simplified version).
    
    Args:
        state (State): Current workflow state
        
    Returns:
        State: Updated state with posting results
    """
    return {**state, "instagram_result": {"status": "skipped", "message": "已跳過 Instagram 發布"}}

def skip_instagram(state: State) -> State:
    """
    Skip posting to Instagram but provide info about generated files.
    
    Args:
        state (State): Current workflow state
        
    Returns:
        State: Same state with skipped info
    """
    images = state.get("images", {})
    
    # Print information about generated files
    print("\n=== 生成的檔案 ===")
    print(f"封面 SVG: {images.get('cover_image', '').replace('.png', '.svg')}")
    
    content_images = images.get('content_images', [])
    for i, img in enumerate(content_images):
        print(f"內容頁 {i+1}: {img.replace('.png', '.svg')}")
    
    print(f"\n所有檔案已保存在: {OUTPUT_DIR}")
    print("請使用瀏覽器或 SVG 查看器直接開啟這些 SVG 檔案")
    
    return {**state, "instagram_result": {
        "status": "skipped",
        "message": "已生成 SVG 檔案，跳過 Instagram 發布"
    }}

def build_workflow() -> StateGraph:
    """
    Build the simplified Langgraph workflow.
    
    Returns:
        StateGraph: Compiled workflow
    """
    # Create a new graph
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("determine_content_type", determine_content_type)
    workflow.add_node("search_ai_news", search_ai_news)
    workflow.add_node("generate_ai_news_content", generate_ai_news_content)
    workflow.add_node("generate_images", generate_images)
    workflow.add_node("skip_instagram", skip_instagram)
    
    # Add edges - simplified flow
    workflow.add_edge("determine_content_type", "search_ai_news")
    workflow.add_edge("search_ai_news", "generate_ai_news_content")
    workflow.add_edge("generate_ai_news_content", "generate_images")
    workflow.add_edge("generate_images", "skip_instagram")
    workflow.add_edge("skip_instagram", END)
    
    # Set entry point
    workflow.set_entry_point("determine_content_type")
    
    return workflow.compile()

def main():
    """Main function to run the workflow."""
    print("開始 Instagram 人工智慧新聞生成工作流程 (簡化版)...")
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Ensure data directory exists for title tracking
    os.makedirs("instagram_poster/data", exist_ok=True)
    
    # Ensure prompts directory exists
    os.makedirs("instagram_poster/prompts", exist_ok=True)
    
    # Build and run the workflow
    workflow = build_workflow()
    result = workflow.invoke({})
    
    print("\n工作流程已完成！")
    print(f"生成的內容類型: {result.get('content', {}).get('content_type', '未知')}")
    print(f"標題: {result.get('content', {}).get('title', '未知')}")
    print(f"內容頁面數量: {len(result.get('content', {}).get('content', []))}")
    
    print("\n您可以在以下位置找到生成的 SVG 檔案:")
    print(f"  {OUTPUT_DIR}")
    
    return result

if __name__ == "__main__":
    main()