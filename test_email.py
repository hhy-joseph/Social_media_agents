#!/usr/bin/env python3
"""
Test script to verify email notification functionality
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the workflow
from app.app import InstagramContentWorkflow

async def test_email_notification():
    """Test email notification with mock data"""
    
    # Get email settings from environment
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")
    recipient_email = os.getenv("NOTIFICATION_EMAIL")
    
    print(f"Email user: {email_user}")
    print(f"Recipient email: {recipient_email}")
    print(f"Email password configured: {'Yes' if email_password else 'No'}")
    
    if not email_user or not email_password:
        print("Please configure EMAIL_USER and EMAIL_PASSWORD in .env file")
        return
    
    if not recipient_email:
        print("Please configure NOTIFICATION_EMAIL in .env file")
        return
    
    # Create workflow instance
    workflow = InstagramContentWorkflow()
    
    # Test request
    request = "Create a quick test Instagram post about AI trends"
    
    # Run workflow with email notification (no Instagram posting)
    print("\nRunning workflow with email notification...")
    results = await workflow.generate_content(
        request=request,
        recipient_email=recipient_email,
        post_to_instagram=False  # Don't post to Instagram for test
    )
    
    # Print results
    print("\n=== Test Results ===")
    if results:
        print(f"Status: {'Success' if 'error' not in results else 'Error'}")
        
        if 'notification' in results:
            notif = results['notification']
            print(f"Notification sent: {notif.get('sent', False)}")
            if notif.get('sent'):
                print(f"Recipient: {notif.get('recipient')}")
                print(f"Subject: {notif.get('subject')}")
                print(f"Images attached: {notif.get('images_attached', 0)}")
            else:
                print(f"Error: {notif.get('error', 'Unknown error')}")
        else:
            print("No notification status available")
        
        if 'errors' in results:
            print(f"Errors: {results['errors']}")
    else:
        print("Status: Error - No results returned")

if __name__ == "__main__":
    asyncio.run(test_email_notification())