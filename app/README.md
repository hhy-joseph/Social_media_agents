# Instagram Agent

A multi-agent system for Instagram content generation using LangGraph.

## Features

- 🤖 Multi-agent system using LangGraph
- 📝 AI-powered content generation
- 🖼️ Automatic image generation from SVG templates 
- 📧 Email notifications
- 📱 Optional Instagram posting

## Installation

### Basic Installation

```bash
pip install ig_agent
```

### Full Installation (with Instagram posting support)

```bash
pip install "ig_agent[full]"
```

### Development Installation

```bash
git clone https://github.com/yourusername/ig_agent.git
cd ig_agent
pip install -e ".[full]"
```

## Usage

### Command Line

```bash
# Generate content with basic options
ig_agent "Generate a carousel post about AI and data analysis"

# Generate content and send email notification
ig_agent "Generate a carousel post about AI and data analysis" --email your.email@example.com

# Generate content and post to Instagram (requires Instagram credentials)
ig_agent "Generate a carousel post about AI and data analysis" --post

# Specify output directory
ig_agent "Generate a carousel post about AI and data analysis" --output-dir ./my_output

# Run in interactive mode
ig_agent --interactive

# Run as LangGraph pipeline
ig_agent "Generate a carousel post about AI and data analysis" --pipeline
```

### Python API

```python
from ig_agent import InstagramAgent
from langchain_xai import ChatXAI

# Initialize LLM
llm = ChatXAI(model="grok-3-mini-beta")

# Initialize agent
agent = InstagramAgent(
    llm=llm,
    output_dir="./output",
    email_user="your-email@gmail.com",  # Or use environment variables
    email_password="your-password",     # Or use environment variables
)

# Run complete pipeline
results = agent.run_pipeline(
    request="Generate a carousel post about AI and data analysis",
    recipient_email="recipient@example.com",  # Optional
    post_to_instagram=False  # Optional
)

# Or run steps individually
content_json = agent.generate_content("Generate a carousel post about AI and data analysis")
images = agent.generate_images()
notification_status = agent.send_notification("recipient@example.com")
instagram_status = agent.post_to_instagram()
```

## Environment Variables

The following environment variables can be used:

- `EMAIL_USER`: Email username for sending notifications
- `EMAIL_PASSWORD`: Email password for sending notifications
- `INSTAGRAM_USERNAME`: Instagram username for posting
- `INSTAGRAM_PASSWORD`: Instagram password for posting
- `NOTIFICATION_EMAIL`: Default email address for notifications

## Architecture

This system uses LangGraph to orchestrate multiple agents:

1. **Content Agent**: Generates Instagram content including cover, content pages, and caption
2. **Image Agent**: Fills SVG templates with content and converts to PNG images
3. **Notification Agent**: Sends email notification with generated content
4. **Instagram Poster**: (Optional) Posts content to Instagram

## License

MIT License