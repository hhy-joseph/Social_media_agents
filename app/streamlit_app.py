"""
Streamlit web interface for Instagram Content Generation Workflow
"""

import streamlit as st
import os
import sys
from pathlib import Path
import json
from PIL import Image

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from app_minimal import SimpleInstagramWorkflow


def main():
    st.set_page_config(
        page_title="Instagram Content Generator",
        page_icon="📱",
        layout="wide"
    )
    
    st.title("📱 Instagram Content Generation Workflow")
    st.markdown("Generate engaging Instagram content using AI workflow")
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # API Key check
    api_key = st.sidebar.text_input(
        "XAI API Key", 
        type="password",
        value=os.getenv("XAI_API_KEY", ""),
        help="Your XAI API key for content generation"
    )
    
    if api_key:
        os.environ["XAI_API_KEY"] = api_key
    
    # Email configuration
    st.sidebar.subheader("📧 Email Notifications")
    email_user = st.sidebar.text_input(
        "Email User",
        value=os.getenv("EMAIL_USER", ""),
        help="Your email address for sending notifications"
    )
    
    email_password = st.sidebar.text_input(
        "Email Password",
        type="password",
        value=os.getenv("EMAIL_PASSWORD", ""),
        help="App password for your email"
    )
    
    recipient_email = st.sidebar.text_input(
        "Recipient Email",
        help="Email to receive the generated content"
    )
    
    if email_user:
        os.environ["EMAIL_USER"] = email_user
    if email_password:
        os.environ["EMAIL_PASSWORD"] = email_password
    
    # Output directory
    output_dir = st.sidebar.text_input(
        "Output Directory",
        value="output",
        help="Directory to save generated content"
    )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🎯 Content Generation")
        
        # Content request input
        request = st.text_area(
            "Content Request",
            placeholder="Enter your content request here... (e.g., 'Create an Instagram post about AI ethics')",
            height=150,
            help="Describe what kind of Instagram content you want to generate"
        )
        
        # Generation options
        col_opt1, col_opt2 = st.columns(2)
        
        with col_opt1:
            content_only = st.checkbox(
                "Content Only",
                help="Generate only text content, skip image generation"
            )
        
        with col_opt2:
            send_email = st.checkbox(
                "Send Email Notification",
                value=bool(recipient_email),
                help="Send email with generated content"
            )
        
        # Generate button
        if st.button("🚀 Generate Content", type="primary", disabled=not (api_key and request)):
            if not api_key:
                st.error("❌ Please provide an XAI API key")
            elif not request:
                st.error("❌ Please enter a content request")
            else:
                generate_content(
                    request, 
                    content_only, 
                    send_email, 
                    recipient_email, 
                    output_dir
                )
    
    with col2:
        st.header("📊 Status")
        
        # Status information
        if "workflow_status" in st.session_state:
            status = st.session_state.workflow_status
            
            if status == "running":
                st.info("🔄 Workflow running...")
            elif status == "success":
                st.success("✅ Workflow completed!")
            elif status == "error":
                st.error("❌ Workflow failed!")
        else:
            st.info("🔆 Ready to generate content")
        
        # Quick examples
        st.subheader("💡 Example Requests")
        examples = [
            "Create a post about AI ethics in tech",
            "Share tips for machine learning beginners",
            "Explain the latest ChatGPT features", 
            "Post about data science career advice",
            "Discuss the future of artificial intelligence"
        ]
        
        for example in examples:
            if st.button(f"📝 {example}", key=f"example_{hash(example)}"):
                st.session_state.example_request = example
                st.rerun()
        
        # Load example if selected
        if "example_request" in st.session_state:
            request = st.session_state.example_request
            del st.session_state.example_request
    
    # Display results
    if "workflow_result" in st.session_state:
        display_results(st.session_state.workflow_result)


def generate_content(request, content_only, send_email, recipient_email, output_dir):
    """Generate content using the workflow"""
    
    # Update status
    st.session_state.workflow_status = "running"
    
    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize workflow
        status_text.text("🔧 Initializing workflow...")
        progress_bar.progress(20)
        
        workflow = SimpleInstagramWorkflow(output_dir=output_dir)
        
        # Generate content
        status_text.text("🎯 Generating content...")
        progress_bar.progress(40)
        
        if content_only:
            result = workflow.generate_content_only(request)
        else:
            email = recipient_email if send_email else None
            result = workflow.run_complete_workflow(request, email)
        
        progress_bar.progress(100)
        status_text.text("✅ Workflow completed!")
        
        # Store results
        st.session_state.workflow_result = result
        st.session_state.workflow_status = "success" if result["status"] == "success" else "error"
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        st.rerun()
        
    except Exception as e:
        st.session_state.workflow_status = "error"
        st.session_state.workflow_error = str(e)
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Error: {str(e)}")


def display_results(result):
    """Display workflow results"""
    
    st.header("📋 Results")
    
    if result["status"] == "error":
        st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
        return
    
    # Create tabs for different result types
    tabs = ["📝 Content", "🖼️ Images", "📁 Files"]
    if "notification" in result:
        tabs.append("📧 Notification")
    
    tab_objects = st.tabs(tabs)
    
    # Content tab
    with tab_objects[0]:
        if "content" in result:
            content = result["content"]
            
            # Cover information
            cover = content.get("cover", {})
            st.subheader("🎭 Cover")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Hashtag", f"#{cover.get('hashtag', 'N/A')}")
                st.write(f"**Heading:** {cover.get('heading_line1', '')} {cover.get('heading_line2', '')}")
            
            with col2:
                st.write(f"**Description:** {cover.get('grey_box_text', 'N/A')}")
            
            # Caption
            st.subheader("📝 Caption")
            st.text_area("Generated Caption", content.get("caption", ""), height=150, disabled=True)
            
            # Content pages
            st.subheader("📄 Content Pages")
            pages = content.get("content_pages", [])
            
            for i, page in enumerate(pages, 1):
                with st.expander(f"Page {i}: {page.get('title', 'Untitled')}"):
                    st.write(page.get("main_point", "No content"))
            
            # Engagement hooks
            if "engagement_hooks" in content:
                hooks = content["engagement_hooks"]
                st.subheader("🎣 Engagement Hooks")
                st.write(f"**Question:** {hooks.get('question_for_comments', 'N/A')}")
                st.write(f"**Sharing Incentive:** {hooks.get('sharing_incentive', 'N/A')}")
            
            # Raw JSON
            with st.expander("🔍 Raw JSON"):
                st.json(content)
    
    # Images tab
    with tab_objects[1]:
        if "images" in result and result["images"]:
            st.subheader("🖼️ Generated Images")
            
            images = result["images"]
            st.info(f"Generated {len(images)} images")
            
            # Display images in grid
            for img in images:
                if "path" in img and os.path.exists(img["path"]):
                    try:
                        image = Image.open(img["path"])
                        st.image(
                            image, 
                            caption=f"{img.get('type', 'Unknown')} - {img.get('file_name', 'Unknown')}", 
                            use_column_width=True
                        )
                    except Exception as e:
                        st.error(f"Could not display image {img.get('file_name', 'Unknown')}: {str(e)}")
                else:
                    st.warning(f"Image file not found: {img.get('path', 'Unknown path')}")
        else:
            st.info("No images generated")
    
    # Files tab
    with tab_objects[2]:
        st.subheader("📁 Output Files")
        
        if "output_dir" in result:
            output_dir = result["output_dir"]
            st.write(f"**Output Directory:** `{output_dir}`")
            
            # List files in output directory
            if os.path.exists(output_dir):
                files = os.listdir(output_dir)
                if files:
                    for file in files:
                        file_path = os.path.join(output_dir, file)
                        file_size = os.path.getsize(file_path)
                        st.write(f"📄 {file} ({file_size:,} bytes)")
                        
                        # Download button for files
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label=f"⬇️ Download {file}",
                                data=f.read(),
                                file_name=file,
                                mime="application/octet-stream"
                            )
                else:
                    st.info("No files found in output directory")
            else:
                st.warning("Output directory not found")
    
    # Notification tab (if present)
    if "notification" in result:
        with tab_objects[3]:
            st.subheader("📧 Email Notification")
            
            notif = result["notification"]
            if notif.get("sent"):
                st.success(f"✅ Email sent successfully to {notif.get('recipient')}")
                st.write(f"**Subject:** {notif.get('subject')}")
                st.write(f"**Images Attached:** {notif.get('images_attached', 0)}")
            else:
                st.error(f"❌ Email failed: {notif.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()