# Instagram Content Generation Workflow

An AI-powered Instagram content generation system built with **LangGraph workflow patterns** that creates engaging posts with visual content.

## 🚀 What's New in v0.2.0

**Major Refactoring**: Moved from agentic supervisor pattern to **LangGraph workflow-based architecture** following industry best practices.

### Key Changes:
- **Workflow-based**: Sequential, predictable content generation pipeline
- **Simplified State Management**: Clear state tracking throughout the process
- **Better Error Handling**: Graceful failure handling at each step
- **Modular Design**: Easy to extend and maintain
- **Multiple Interfaces**: CLI, Python API, and Streamlit web interface

## Features

- **🤖 AI Content Generation**: Creates engaging Instagram captions and structured content using advanced prompting
- **🌏 Traditional Chinese Focus**: Optimized for Hong Kong and Taiwan audiences with native language patterns
- **🎨 Automated Image Generation**: Generates images using SVG templates with PIL fallback
- **📧 Email Notifications**: Optional email notifications with content and images (disabled by default)
- **🌐 Web Interface**: Streamlit-based web application for easy content creation
- **⚡ CLI Tool**: Command-line interface for quick generation
- **🔄 Workflow Architecture**: LangGraph-based sequential processing with error handling
- **🎯 Smart Content Strategy**: Psychology-driven content design with engagement hooks

## Content Language & Customization

### Language Requirements
- **Primary Language**: Traditional Chinese (繁體中文)
- **Target Audience**: Hong Kong and Taiwan users
- **Writing Style**: Professional yet approachable, using local terminology
- **Content Types**: Data science fundamentals and AI latest trends

### Content Generation Features
- **Advanced Prompting**: Psychology-driven content creation with engagement hooks
- **Smart Search**: Automatic decision-making for when to search for latest AI news
- **Validation**: Automatic text truncation to meet platform requirements
- **Engagement Optimization**: Questions, sharing incentives, and call-to-actions

## Architecture

The system uses a **workflow-based architecture** with LangGraph:

```
Request Input → Content Generation → Image Generation → Notification → Complete
     ↓              ↓                    ↓                ↓           ↓
   State          State              State            State       Results
```

### Core Components:
1. **State Management**: Tracks workflow progress and data
2. **Content Node**: Generates text content and post structure using advanced prompts
3. **Image Node**: Creates visual content from templates with PIL fallback
4. **Notification Node**: Sends email notifications (optional)
5. **Supervisor Node**: Routes workflow between stages with error handling

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ig_agent
```

2. Install dependencies:
```bash
pip install -e .
# or
uv sync
```

3. Set up environment variables:
```bash
# Create .env file in project root
cp .env.example .env

# Or set environment variables directly:
export XAI_API_KEY="your-xai-api-key"           # Required
export GROK_BASE_URL="https://api.x.ai/v1"     # Required
export EMAIL_USER="your-email@gmail.com"        # Optional
export EMAIL_PASSWORD="your-app-password"       # Optional
export NOTIFICATION_EMAIL="recipient@example.com"  # Optional
```

## Usage

### 🌐 Web Interface (Recommended)

Launch the Streamlit web app:

```bash
streamlit run app/streamlit_app.py
```

Then open your browser to `http://localhost:8501`

### ⚡ Command Line Interface

Quick content generation:

```bash
# Basic usage
python cli.py "Create a post about AI ethics"

# With email notification
python cli.py "Share ML tips" --email user@example.com

# Content only (no images)
python cli.py "Post about data science" --content-only

# Custom output directory
python cli.py "AI trends 2024" --output ./my_content
```

### 🔧 Python API

#### Simple Workflow (Recommended)

```python
from app.app_minimal import SimpleInstagramWorkflow

# Initialize workflow
workflow = SimpleInstagramWorkflow(output_dir="./output")

# Generate content with images
result = workflow.run_complete_workflow(
    request="Create a post about AI ethics",
    recipient_email="user@example.com"  # Optional
)

# Check results
if result["status"] == "success":
    print(f"Generated {len(result['images'])} images")
    print(f"Output saved to: {result['output_dir']}")
```

#### Advanced Async Workflow

```python
import asyncio
from app.app import InstagramContentWorkflow

async def main():
    workflow = InstagramContentWorkflow()
    
    result = await workflow.generate_content(
        request="Create engaging AI content",
        recipient_email="user@example.com",
        post_to_instagram=False
    )
    
    return result

# Run async workflow
result = asyncio.run(main())
```

## Configuration

### Required Environment Variables

```bash
# AI Model Configuration (Choose one)
XAI_API_KEY="your-xai-api-key"          # For Grok models (Recommended)
GROK_BASE_URL="https://api.x.ai/v1"     # XAI API base URL
# OR
OPENAI_API_KEY="your-openai-api-key"    # For OpenAI models
```

### Optional Environment Variables

```bash
# Email Notifications (Disabled by default)
EMAIL_USER="your-email@gmail.com"        # Sender email address
EMAIL_PASSWORD="your-app-password"       # Gmail app-specific password (not regular password)
NOTIFICATION_EMAIL="recipient@example.com"  # Default recipient

# Instagram Posting
UPLOAD_TO_IG=False                       # Enable/disable Instagram posting
INSTAGRAM_USERNAME="your-username"       # Instagram username
INSTAGRAM_PASSWORD="your-password"       # Instagram password
```

### Email Configuration Setup

Email notifications are **disabled by default**. To enable them:

1. **Generate Gmail App Password**:
   - Go to Google Account Settings → Security → 2-Step Verification
   - Generate an "App Password" for this application
   - Use this password, not your regular Gmail password

2. **Configure Environment Variables**:
   ```bash
   EMAIL_USER="your-email@gmail.com"
   EMAIL_PASSWORD="your-16-character-app-password"
   NOTIFICATION_EMAIL="recipient@example.com"
   ```

3. **Enable in Code**:
   ```python
   # In your code, pass recipient_email to enable notifications
   result = await workflow.generate_content(
       request="Your request",
       recipient_email=os.getenv("NOTIFICATION_EMAIL")  # Enable notifications
   )
   ```

### Directory Structure

```
app/
   ig_agent/
      agents/              # Content and image generation agents
      static/              # SVG templates for image generation
      prompts/             # AI prompts for content generation
   app.py                   # Main async workflow
   app_minimal.py           # Simple synchronous workflow
   graph.py                # LangGraph workflow definition
   state.py                # Workflow state management
   configuration.py        # Configuration management
   streamlit_app.py        # Web interface
   tools_and_schemas.py    # Pydantic models and validation
   utils.py                # Utility functions
cli.py                     # Command-line interface
```

## Output Structure

Generated content is organized in timestamped directories:

```
output/
   2024-07-15/
       20240715_143022/
           content.json     # Structured content data
           cover.png        # Cover image
           content_1.png    # Content page 1
           content_2.png    # Content page 2
           ...
```

### Content JSON Structure

```json
{
  "content_type": "AI領域最新動態",
  "search_decision": {
    "performed_search": true,
    "search_keywords": ["AI breakthrough", "GPT-5"],
    "search_reason": "需要搜索最新AI突破資訊"
  },
  "cover": {
    "hashtag": "AI突破",
    "heading_line1": "AI革命來臨",
    "heading_line2": "你準備好了嗎？",
    "grey_box_text": "AI將改變一切工作方式"
  },
  "caption": "你知道嗎？AI正以前所未有的速度改變我們的世界...",
  "content_pages": [
    {
      "title": "最新AI模型突破",
      "main_point": "詳細解釋最新AI技術如何應用於實際工作中..."
    }
  ],
  "engagement_hooks": {
    "question_for_comments": "你認為AI會如何改變你的工作？",
    "sharing_incentive": "分享給同事，一起探討AI的未來發展"
  },
  "sources": ["https://openai.com/blog/..."]
}
```

### Content Generation Process

1. **Language**: All content is generated in Traditional Chinese (繁體中文)
2. **Search Intelligence**: Automatically decides when to search for latest AI news
3. **Validation**: All text fields are automatically truncated to meet Instagram limits
4. **Engagement**: Built-in psychology-driven hooks for comments and shares
5. **Customization**: Easily modify prompts in `app/ig_agent/prompts/content_generation.txt`

## Development

### Project Structure

```
ig_agent/
   app/                     # Workflow-based application
      ig_agent/
         agents/          # Content and image generation agents
         static/          # SVG templates
         prompts/         # AI prompt templates
      *.py                # Workflow components and interfaces
   cli.py                   # Command-line interface
   pyproject.toml          # Dependencies and project config
   README.md               # This file
```

### Running Tests

```bash
# Test CLI
python cli.py "Test content generation" --content-only

# Test web interface
streamlit run app/streamlit_app.py

# Test Python API
python -c "
from app.app_minimal import SimpleInstagramWorkflow
workflow = SimpleInstagramWorkflow()
result = workflow.generate_content_only('Test request')
print(result['status'])
"
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the workflow pattern
4. Test with CLI, web interface, and Python API
5. Submit a pull request

## Migration Guide

If upgrading from v0.1.0 (agentic system):

### Old Usage (v0.1.0)
```python
from ig_agent.instagram_agent import InstagramAgent
agent = InstagramAgent(llm=llm)
result = agent.run_pipeline(request)
```

### New Usage (v0.2.0)
```python
from app.app_minimal import SimpleInstagramWorkflow
workflow = SimpleInstagramWorkflow()
result = workflow.run_complete_workflow(request)
```

## Troubleshooting

### Common Issues

1. **Missing API Key**
   ```bash
   # For XAI/Grok (recommended)
   export XAI_API_KEY="your-xai-key-here"
   export GROK_BASE_URL="https://api.x.ai/v1"
   
   # Or for OpenAI
   export OPENAI_API_KEY="your-openai-key-here"
   ```

2. **Email Notifications Not Working**
   - Ensure `EMAIL_USER` and `EMAIL_PASSWORD` are set
   - Use Gmail **app-specific password**, not regular password
   - Enable 2-factor authentication on Gmail first
   - Pass `recipient_email` parameter to enable notifications

3. **Validation Errors (String Too Long)**
   - The system now automatically truncates text to meet Instagram limits
   - Check content generation logs for truncation messages
   - Modify prompt if you want shorter default content

4. **Images Not Generating**
   - Check that SVG templates exist in `app/ig_agent/static/`
   - Verify templates are valid SVG files
   - PIL (Pillow) is used as fallback for image generation
   - Cairo library warnings can be ignored (PIL fallback works)

5. **DuckDuckGo Search Rate Limits**
   - This is normal and expected
   - System falls back to knowledge base when search fails
   - Rate limits reset automatically after some time

6. **Import Errors**
   - Run `pip install -e .` to install in development mode
   - Check Python path includes the project directory
   - Ensure all dependencies are installed with `uv sync`

### Getting Help

- Check the `app/streamlit_app.py` examples
- Run `python cli.py --help` for CLI options
- Look at workflow logs for debugging

## Docker Deployment

### Building the Docker Image

1. **Build the image**:
```bash
docker build -t ig-agent:latest .
```

2. **Run the container**:
```bash
# Basic usage
docker run --rm -e XAI_API_KEY="your-xai-key" ig-agent:latest python cli.py "Create AI content"

# With volume for persistent output
docker run --rm -v $(pwd)/output:/app/output -e XAI_API_KEY="your-xai-key" ig-agent:latest python cli.py "Create AI content"

# Run Streamlit web interface
docker run --rm -p 8501:8501 -e XAI_API_KEY="your-xai-key" ig-agent:latest streamlit run app/streamlit_app.py --server.address 0.0.0.0
```

3. **Environment variables for Docker**:
```bash
# Required
-e XAI_API_KEY="your-xai-key"
-e GROK_BASE_URL="https://api.x.ai/v1"

# Optional
-e EMAIL_USER="your-email@gmail.com"
-e EMAIL_PASSWORD="your-app-password"
-e NOTIFICATION_EMAIL="recipient@example.com"
```

### AWS Lambda Deployment (Optional)

For serverless deployment on AWS Lambda, follow these guidelines:

#### Prerequisites
- AWS CLI configured
- Docker installed
- AWS Lambda container image support

#### Step 1: Create Lambda-compatible Dockerfile
```dockerfile
# Create Dockerfile.lambda
FROM public.ecr.aws/lambda/python:3.12

# Install system dependencies
RUN yum update -y && yum install -y \
    cairo-devel \
    gobject-introspection-devel \
    gcc \
    && yum clean all

# Copy application code
COPY app/ ${LAMBDA_TASK_ROOT}/app/
COPY cli.py ${LAMBDA_TASK_ROOT}/
COPY pyproject.toml uv.lock ${LAMBDA_TASK_ROOT}/

# Install Python dependencies
RUN pip install uv && uv sync --frozen --no-cache

# Set Lambda handler
CMD ["lambda_handler.lambda_handler"]
```

#### Step 2: Create Lambda Handler
```python
# Create lambda_handler.py
import json
import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app_minimal import SimpleInstagramWorkflow

def lambda_handler(event, context):
    """
    AWS Lambda handler for Instagram content generation
    
    Expected event structure:
    {
        "request": "Content generation request",
        "email": "optional-email@example.com",
        "content_only": false
    }
    """
    
    try:
        # Parse request
        request = event.get("request", "")
        email = event.get("email")
        content_only = event.get("content_only", False)
        
        if not request:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Request parameter is required"})
            }
        
        # Initialize workflow
        workflow = SimpleInstagramWorkflow(output_dir="/tmp/output")
        
        # Generate content
        if content_only:
            result = workflow.generate_content_only(request)
        else:
            result = workflow.run_complete_workflow(request, email)
        
        # Return success response
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "result": result
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "error": str(e)
            })
        }
```

#### Step 3: Build and Deploy
```bash
# Build Lambda container image
docker build -f Dockerfile.lambda -t ig-agent-lambda .

# Tag for ECR
docker tag ig-agent-lambda:latest YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/ig-agent-lambda:latest

# Push to ECR
aws ecr get-login-password --region YOUR_REGION | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com
docker push YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/ig-agent-lambda:latest

# Create Lambda function
aws lambda create-function \
    --function-name ig-agent \
    --package-type Image \
    --code ImageUri=YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/ig-agent-lambda:latest \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
    --timeout 900 \
    --memory-size 1024 \
    --environment Variables='{XAI_API_KEY=your-xai-key,GROK_BASE_URL=https://api.x.ai/v1}'
```

#### Step 4: Test Lambda Function
```bash
# Test via AWS CLI
aws lambda invoke \
    --function-name ig-agent \
    --payload '{"request": "Create AI content about machine learning"}' \
    response.json

# Check response
cat response.json
```

#### Lambda Deployment Notes
- **Memory**: Recommend 1024MB+ for image generation
- **Timeout**: Set to 900 seconds (15 minutes) for complete workflow
- **Environment**: Store API keys in Lambda environment variables
- **Storage**: Use `/tmp` for temporary files (512MB limit)
- **Cold Start**: First invocation may take 10-30 seconds
- **Costs**: Pay per invocation, more cost-effective for occasional use

#### Alternative: Lambda Layers
For smaller deployments, consider using Lambda Layers instead of containers:

```bash
# Create layer with dependencies
mkdir python
pip install -r requirements.txt -t python/
zip -r dependencies.zip python/

# Upload as Lambda layer
aws lambda publish-layer-version \
    --layer-name ig-agent-dependencies \
    --zip-file fileb://dependencies.zip \
    --compatible-runtimes python3.12
```

## License

MIT License - see LICENSE file for details