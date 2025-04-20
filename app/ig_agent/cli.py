"""
Command-line interface for Instagram Agent
"""

import os
import argparse
import logging
from pathlib import Path
from datetime import datetime

def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(description="Instagram Agent - Multi-agent system for Instagram content generation")
    
    # Main arguments
    parser.add_argument('request', type=str, help='Content generation request', nargs='?')
    parser.add_argument('--output-dir', type=str, help='Directory to save output files')
    parser.add_argument('--email', type=str, help='Email address to send notification to')
    parser.add_argument('--post', action='store_true', help='Post to Instagram after generation')
    
    # Configuration arguments
    parser.add_argument('--model', type=str, default='grok-3-mini-beta', help='LLM model to use')
    parser.add_argument('--prompts-dir', type=str, help='Directory containing prompt files')
    parser.add_argument('--templates-dir', type=str, help='Directory containing SVG templates')
    
    # Mode arguments
    parser.add_argument('--pipeline', action='store_true', help='Run as LangGraph pipeline')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    
    # Logging arguments
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger("ig_agent")
    
    # Create output directory with timestamp if not provided
    if not args.output_dir:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output_dir = Path(f"output_{timestamp}")
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize LLM
    try:
        from langchain_xai import ChatXAI
        llm = ChatXAI(model=args.model)
        logger.info(f"Initialized LLM: {args.model}")
    except ImportError:
        logger.error("langchain_xai is required. Install with: pip install langchain_xai")
        return 1
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {str(e)}")
        return 1
    
    # Run in pipeline mode
    if args.pipeline:
        if not args.request:
            logger.error("Request is required in pipeline mode")
            return 1
        
        try:
            from ig_agent.pipeline import create_pipeline
            
            pipeline = create_pipeline(
                llm=llm,
                output_dir=args.output_dir,
                prompts_dir=args.prompts_dir,
                templates_dir=args.templates_dir,
                email_user=os.environ.get("EMAIL_USER"),
                email_password=os.environ.get("EMAIL_PASSWORD")
            )
            
            inputs = {
                "messages": [
                    {
                        "role": "user", 
                        "content": args.request
                    }
                ]
            }
            
            logger.info("Running pipeline...")
            for output in pipeline.stream(inputs):
                if "__end__" not in output:
                    step = list(output.keys())[-1]
                    logger.info(f"Step: {step}")
                    if step in ["content_agent", "image_agent", "notification_agent"]:
                        logger.info(f"Message from {step}: {output[step]['messages'][-1].content}")
            
            logger.info(f"Pipeline completed. Output directory: {args.output_dir}")
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            return 1
    
    # Run in standard mode (default)
    elif not args.interactive:
        if not args.request:
            logger.error("Request is required in standard mode")
            return 1
        
        try:
            from ig_agent.instagram_agent import InstagramAgent
            
            agent = InstagramAgent(
                llm=llm,
                output_dir=args.output_dir,
                prompts_dir=args.prompts_dir,
                templates_dir=args.templates_dir,
                email_user=os.environ.get("EMAIL_USER"),
                email_password=os.environ.get("EMAIL_PASSWORD"),
                instagram_username=os.environ.get("INSTAGRAM_USERNAME"),
                instagram_password=os.environ.get("INSTAGRAM_PASSWORD")
            )
            
            results = agent.run_pipeline(
                request=args.request,
                recipient_email=args.email,
                post_to_instagram=args.post
            )
            
            logger.info(f"Process completed. Output directory: {results['output_dir']}")
            logger.info(f"Generated {len(results['images'])} images")
            
            if 'notification' in results:
                logger.info(f"Notification: {results['notification']['sent']}")
            
            if 'instagram' in results:
                logger.info(f"Instagram post: {results['instagram']['posted']}")
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return 1
    
    # Run in interactive mode
    else:
        try:
            from ig_agent.instagram_agent import InstagramAgent
            
            agent = InstagramAgent(
                llm=llm,
                output_dir=args.output_dir,
                prompts_dir=args.prompts_dir,
                templates_dir=args.templates_dir,
                email_user=os.environ.get("EMAIL_USER"),
                email_password=os.environ.get("EMAIL_PASSWORD"),
                instagram_username=os.environ.get("INSTAGRAM_USERNAME"),
                instagram_password=os.environ.get("INSTAGRAM_PASSWORD")
            )
            
            print("Instagram Agent Interactive Mode")
            print("--------------------------------")
            print("Type 'exit' to quit")
            
            while True:
                request = input("\nEnter content request: ").strip()
                
                if request.lower() == 'exit':
                    break
                
                if not request:
                    continue
                
                try:
                    # Generate content
                    print("\nGenerating content...")
                    content_json = agent.generate_content(request)
                    print(f"Content generated with {len(content_json.get('content_pages', []))} pages")
                    
                    # Generate images
                    print("\nGenerating images...")
                    images = agent.generate_images()
                    print(f"Generated {len(images)} images")
                    
                    # Ask about notification
                    send_notification = input("\nSend email notification? (y/n): ").lower().startswith('y')
                    if send_notification:
                        email = input("Email address: ").strip()
                        if email:
                            notification_status = agent.send_notification(email)
                            print(f"Notification sent: {notification_status['sent']}")
                    
                    # Ask about posting to Instagram
                    post_to_instagram = input("\nPost to Instagram? (y/n): ").lower().startswith('y')
                    if post_to_instagram:
                        instagram_status = agent.post_to_instagram()
                        print(f"Posted to Instagram: {instagram_status['posted']}")
                    
                    print(f"\nOutput directory: {agent.output_dir}")
                    
                except Exception as e:
                    print(f"Error: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in interactive mode: {str(e)}")
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main())