#!/usr/bin/env python3
"""
Command Line Interface for Instagram Content Generation Workflow

This CLI provides a simple interface to the refactored workflow system.
"""

import argparse
import sys
import os
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from app_minimal import SimpleInstagramWorkflow


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Instagram Content Generation Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py "Create a post about AI ethics"
  python cli.py "Share tips about machine learning" --email user@example.com
  python cli.py "Post about data science trends" --output ./my_output
        """
    )
    
    parser.add_argument(
        "request",
        help="Content generation request/prompt"
    )
    
    parser.add_argument(
        "--email",
        help="Email address to send notification to (requires EMAIL_USER and EMAIL_PASSWORD env vars)"
    )
    
    parser.add_argument(
        "--output",
        default="output",
        help="Output directory (default: output)"
    )
    
    parser.add_argument(
        "--content-only",
        action="store_true",
        help="Generate content only (skip images)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        print("Please set it with: export OPENAI_API_KEY=your_api_key")
        sys.exit(1)
    
    # Initialize workflow
    print(f"🚀 Starting Instagram content generation workflow...")
    print(f"📝 Request: {args.request}")
    
    workflow = SimpleInstagramWorkflow(output_dir=args.output)
    
    try:
        if args.content_only:
            # Generate content only
            print("🎯 Generating content only...")
            result = workflow.generate_content_only(args.request)
        else:
            # Run complete workflow
            print("🔄 Running complete workflow...")
            result = workflow.run_complete_workflow(args.request, args.email)
        
        # Display results
        if result["status"] == "success":
            print("✅ Workflow completed successfully!")
            
            if "content" in result:
                content = result["content"]
                cover = content.get("cover", {})
                print(f"📱 Topic: {cover.get('heading_line1', 'N/A')} {cover.get('heading_line2', '')}")
                print(f"🏷️  Hashtag: #{cover.get('hashtag', 'N/A')}")
                print(f"📄 Content Pages: {len(content.get('content_pages', []))}")
            
            if "images" in result:
                print(f"🖼️  Images Generated: {len(result['images'])}")
            
            if "output_dir" in result:
                print(f"📁 Output Directory: {result['output_dir']}")
            
            if "notification" in result:
                notif = result["notification"]
                if notif.get("sent"):
                    print(f"📧 Notification sent to: {notif.get('recipient')}")
                else:
                    print(f"📧 Notification failed: {notif.get('error')}")
            
            if "workflow_steps" in result:
                steps = result["workflow_steps"]
                print(f"🔧 Workflow Steps:")
                print(f"   Content: {steps.get('content_generation', 'unknown')}")
                print(f"   Images: {steps.get('image_generation', 'unknown')}")
                print(f"   Notification: {steps.get('notification', 'unknown')}")
        
        else:
            print("❌ Workflow failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⏹️  Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()