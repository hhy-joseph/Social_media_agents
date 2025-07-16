#!/usr/bin/env python3
"""
Simple terminal interface for Instagram Agent
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app import InstagramContentWorkflow

async def main():
    """Run Instagram content generation from terminal"""
    
    # Get user input
    if len(sys.argv) > 1:
        request = " ".join(sys.argv[1:])
    else:
        request = input("Enter your content request: ")
    
    # Ask about Instagram posting
    post_to_ig = input("Post to Instagram? (y/n): ").lower().startswith('y')
    
    # Optional email for notifications
    email = input("Email for notifications (optional): ").strip()
    if not email:
        email = None
    
    print(f"\n🚀 Generating content for: {request}")
    print(f"📱 Instagram posting: {'Yes' if post_to_ig else 'No'}")
    if email:
        print(f"📧 Notifications: {email}")
    print("-" * 50)
    
    # Create workflow instance
    workflow = InstagramContentWorkflow()
    
    # Run workflow
    results = await workflow.generate_content(
        request=request,
        post_to_instagram=post_to_ig,
        recipient_email=email
    )
    
    # Print results
    print("\n=== Results ===")
    if results:
        print(f"✅ Status: {'Success' if 'error' not in results else 'Error'}")
        
        if 'content' in results and results['content']:
            content = results['content']
            print(f"📝 Topic: {content.get('cover', {}).get('heading_line1', 'N/A')}")
            print(f"🏷️ Hashtag: #{content.get('cover', {}).get('hashtag', 'N/A')}")
            print(f"📄 Content pages: {len(content.get('content_pages', []))}")
        
        if 'images' in results and results['images']:
            print(f"🖼️ Images generated: {len(results['images'])}")
        
        if 'output_dir' in results:
            print(f"📁 Output saved to: {results['output_dir']}")
        
        if 'instagram' in results:
            insta = results['instagram']
            status = insta.get('status') == 'success' if 'status' in insta else insta.get('posted', False)
            print(f"📱 Instagram posted: {'✅ Yes' if status else '❌ No'}")
            if 'url' in insta:
                print(f"🔗 Post URL: {insta['url']}")
        
        if 'notification' in results:
            notif = results['notification']
            print(f"📧 Notification sent: {'✅ Yes' if notif.get('sent', False) else '❌ No'}")
        
        if 'errors' in results and results['errors']:
            print(f"⚠️ Errors: {results['errors']}")
    else:
        print("❌ Error: No results returned")

if __name__ == "__main__":
    asyncio.run(main())