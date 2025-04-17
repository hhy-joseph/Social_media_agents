import os
from typing import Dict, Any
from dotenv import load_dotenv

from langgraph.graph import StateGraph

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
    return {**state, "content": content}

def generate_images(state: State) -> State:
    """
    Generate images based on content.
    
    Args:
        state (State): Current workflow state
        
    Returns:
        State: Updated state with image paths
    """
    content = state.get("content", {})
    images = image_agent.generate_images(content)
    return {**state, "images": images}

def should_post_to_instagram(state: State) -> str:
    """
    Decide whether to post to Instagram based on environment variable.
    
    Args:
        state (State): Current workflow state
        
    Returns:
        str: Next node to execute
    """
    # Check environment variable for Instagram posting
    upload_to_ig = os.getenv("UPLOAD_TO_IG", "False").lower() in ("true", "1", "yes")
    
    if upload_to_ig:
        print("環境變數 UPLOAD_TO_IG 設置為 True，將發布到 Instagram。")
        return "post_to_instagram"
    else:
        print("環境變數 UPLOAD_TO_IG 設置為 False，跳過 Instagram 發布。")
        return "skip_instagram"

def post_to_instagram(state: State) -> State:
    """
    Post content to Instagram.
    
    Args:
        state (State): Current workflow state
        
    Returns:
        State: Updated state with posting results
    """
    content = state.get("content", {})
    images = state.get("images", {})
    
    result = instagram_agent.upload_post(
        image_paths=images.get("all_images", []),
        caption=content.get("description", "查看我們的最新人工智慧研究動態！")
    )
    
    return {**state, "instagram_result": result}

def skip_instagram(state: State) -> State:
    """
    Skip posting to Instagram but provide info about generated content.
    
    Args:
        state (State): Current workflow state
        
    Returns:
        State: Same state with skipped info
    """
    print("已跳過 Instagram 發布。生成的圖片保存在:", OUTPUT_DIR)
    
    return {**state, "instagram_result": {
        "status": "skipped",
        "message": "已跳過 Instagram 發布，因為 UPLOAD_TO_IG 設置為 False"
    }}

def build_workflow() -> StateGraph:
    """
    Build the Langgraph workflow.
    
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
    workflow.add_node("post_to_instagram", post_to_instagram)
    workflow.add_node("skip_instagram", skip_instagram)
    
    # Add conditional router
    workflow.add_conditional_edges(
        "generate_images",
        should_post_to_instagram,
        {
            "post_to_instagram": "post_to_instagram",
            "skip_instagram": "skip_instagram"
        }
    )
    
    # Add edges - simplified flow always going through AI news path
    workflow.add_edge("determine_content_type", "search_ai_news")
    workflow.add_edge("search_ai_news", "generate_ai_news_content")
    workflow.add_edge("generate_ai_news_content", "generate_images")
    
    # Set entry and exit points
    workflow.set_entry_point("determine_content_type")
    workflow.add_terminal_node("post_to_instagram")
    workflow.add_terminal_node("skip_instagram")
    
    return workflow.compile()

def main():
    """Main function to run the workflow."""
    print("開始 Instagram 人工智慧新聞生成和發佈工作流程...")
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Ensure data directory exists for title tracking
    os.makedirs("instagram_poster/data", exist_ok=True)
    
    # Ensure prompts directory exists
    os.makedirs("instagram_poster/prompts", exist_ok=True)
    
    # Check Instagram upload setting
    upload_to_ig = os.getenv("UPLOAD_TO_IG", "False").lower() in ("true", "1", "yes")
    print(f"Instagram 發佈設置: {'啟用' if upload_to_ig else '禁用'}")
    
    # Build and run the workflow
    workflow = build_workflow()
    result = workflow.invoke({})
    
    print("\n工作流程已完成！")
    print(f"生成的內容類型: {result.get('content', {}).get('content_type', '未知')}")
    print(f"標題: {result.get('content', {}).get('title', '未知')}")
    print(f"內容頁面數量: {len(result.get('content', {}).get('content', []))}")
    
    instagram_result = result.get('instagram_result', {})
    if instagram_result.get('status') == 'skipped':
        print(f"Instagram 發佈: 已跳過 (圖片已保存至 {OUTPUT_DIR})")
    else:
        print(f"Instagram 發佈結果: {instagram_result.get('status', '未知')}")
    
    return result

if __name__ == "__main__":
    main()