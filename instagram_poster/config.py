import os
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Instagram credentials - prioritize environment variables
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "your_instagram_username")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "your_instagram_password")

# Upload to Instagram control
UPLOAD_TO_INSTAGRAM = os.getenv("UPLOAD_TO_IG", "False").lower() in ("true", "1", "yes")

# LLM Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "grok-2-1212")

# Content settings
MAX_PAGES = int(os.getenv("MAX_PAGES", "7"))  # Maximum number of content pages

# File paths - updated to use the actual template paths
COVER_TEMPLATE_PATH = "instagram_poster/static/cover-template.svg"
CONTENT_TEMPLATE_PATH = "instagram_poster/static/content-template.svg"
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "instagram_poster/output")

def ensure_templates_exist():
    """Ensure template files exist by copying from app/static if necessary."""
    # Create static directory if it doesn't exist
    os.makedirs("instagram_poster/static", exist_ok=True)
    
    # Check if app/static templates exist
    app_cover_path = "app/static/cover-template.svg"
    app_content_path = "app/static/content-template.svg"
    
    # Copy templates if they exist in app/static but not in instagram_poster/static
    if os.path.exists(app_cover_path) and not os.path.exists(COVER_TEMPLATE_PATH):
        shutil.copy(app_cover_path, COVER_TEMPLATE_PATH)
        print(f"Copied cover template from {app_cover_path} to {COVER_TEMPLATE_PATH}")
    
    if os.path.exists(app_content_path) and not os.path.exists(CONTENT_TEMPLATE_PATH):
        shutil.copy(app_content_path, CONTENT_TEMPLATE_PATH)
        print(f"Copied content template from {app_content_path} to {CONTENT_TEMPLATE_PATH}")
    
    # Create default templates if they don't exist
    if not os.path.exists(CONTENT_TEMPLATE_PATH):
        with open(CONTENT_TEMPLATE_PATH, "w", encoding="utf-8") as f:
            f.write("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080">
  <!-- Background -->
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#121212" />
      <stop offset="100%" stop-color="#232323" />
    </linearGradient>
    
    <linearGradient id="contentGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#262626" />
      <stop offset="100%" stop-color="#1A1A1A" />
    </linearGradient>
    
    <!-- Highlight box gradient -->
    <linearGradient id="highlightGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#4B9CD3" />
      <stop offset="100%" stop-color="#3A7CA5" />
    </linearGradient>
  </defs>
  
  <!-- Main background -->
  <rect width="1080" height="1080" fill="url(#bgGradient)" />
  
  <!-- Subtle grid pattern -->
  <path d="M0,0 L1080,0 L1080,1080 L0,1080 Z" fill="none" stroke="#333333" stroke-width="0.5" stroke-dasharray="2,20" />
  <path d="M0,0 L1080,0 L1080,1080 L0,1080 Z" fill="none" stroke="#333333" stroke-width="0.5" stroke-dasharray="2,20" transform="rotate(90, 540, 540)" />
  
  <!-- Decorative elements -->
  <g opacity="0.3">
    <!-- Data flow lines in background -->
    <path d="M0,200 Q200,250 400,150 T800,220 T1080,180" stroke="#4B9CD3" stroke-width="2" fill="none" />
    <path d="M0,300 Q300,400 500,350 T900,420 T1080,380" stroke="#4B9CD3" stroke-width="1.5" fill="none" />
    <path d="M0,900 Q200,850 400,900 T800,850 T1080,920" stroke="#4B9CD3" stroke-width="2.5" fill="none" />
  </g>
  
  <!-- Main content container -->
  <rect x="140" y="120" width="800" height="840" rx="12" ry="12" fill="url(#contentGradient)" />
  
  <!-- Account name in top right -->
  <text x="820" y="160" font-family="PingFang TC, Microsoft JhengHei, sans-serif" font-size="20" font-weight="500" fill="#AAAAAA" text-anchor="end" id="account">@datasci_daily</text>
  
  <!-- Title -->
  <text x="190" y="240" font-family="PingFang TC, Microsoft JhengHei, sans-serif" font-size="44" font-weight="700" fill="#FFFFFF" id="content-title">在給建議之前</text>
  
  <!-- Divider line -->
  <rect x="190" y="265" width="100" height="5" rx="2.5" ry="2.5" fill="#4B9CD3" />
  
  <!-- Content paragraphs -->
  <text x="190" y="340" font-family="PingFang TC, Microsoft JhengHei, sans-serif" font-size="28" fill="#CCCCCC" id="p1">我想先破除「英文爛就學不好前端」的迷思，</text>
  
  <text x="190" y="400" font-family="PingFang TC, Microsoft JhengHei, sans-serif" font-size="28" fill="#CCCCCC" id="p2">因為當你開始花時間學習就會發現，</text>
  
  <text x="190" y="460" font-family="PingFang TC, Microsoft JhengHei, sans-serif" font-size="28" fill="#CCCCCC" id="p3">前端經常就是那幾十個單字反覆出現，</text>
  
  <text x="190" y="520" font-family="PingFang TC, Microsoft JhengHei, sans-serif" font-size="28" fill="#CCCCCC" id="p4">就算一開始完全看不懂，</text>
  
  <!-- Highlight box for key content -->
  <rect x="140" y="550" width="800" height="80" fill="url(#highlightGradient)" opacity="0.9" id="highlight-box" />
  <text x="190" y="602" font-family="PingFang TC, Microsoft JhengHei, sans-serif" font-size="32" font-weight="600" fill="#FFFFFF" id="highlight-text">只要多看、多查、加上實際寫 Code</text>
  
  <text x="190" y="680" font-family="PingFang TC, Microsoft JhengHei, sans-serif" font-size="28" fill="#CCCCCC" id="p5">其實很快就可以熟悉專有名詞和語法，</text>
  
  <text x="190" y="740" font-family="PingFang TC, Microsoft JhengHei, sans-serif" font-size="28" fill="#CCCCCC" id="p6">加上現在有 ChatGPT 和其他 AI 工具後，</text>
  
  <text x="190" y="800" font-family="PingFang TC, Microsoft JhengHei, sans-serif" font-size="28" fill="#CCCCCC" id="p7">翻譯文件已經比以前容易許多。</text>
</svg>""")
            print(f"Created default content template at {CONTENT_TEMPLATE_PATH}")
    
    if not os.path.exists(COVER_TEMPLATE_PATH):
        with open(COVER_TEMPLATE_PATH, "w", encoding="utf-8") as f:
            f.write("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080">
  <!-- Background -->
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#121212" />
      <stop offset="100%" stop-color="#232323" />
    </linearGradient>
    
    <!-- Abstract data visualization elements -->
    <pattern id="dataPoints" width="100" height="100" patternUnits="userSpaceOnUse">
      <circle cx="10" cy="10" r="1.5" fill="rgba(100,149,237,0.5)" />
      <circle cx="30" cy="40" r="1" fill="rgba(100,149,237,0.4)" />
      <circle cx="55" cy="20" r="2" fill="rgba(100,149,237,0.6)" />
      <circle cx="80" cy="50" r="1.2" fill="rgba(100,149,237,0.5)" />
      <circle cx="20" cy="80" r="1.8" fill="rgba(100,149,237,0.4)" />
      <circle cx="70" cy="75" r="1" fill="rgba(100,149,237,0.5)" />
    </pattern>
  </defs>
  
  <!-- Main background -->
  <rect width="1080" height="1080" fill="url(#bgGradient)" />
  
  <!-- Abstract data visualization background elements -->
  <rect width="1080" height="1080" fill="url(#dataPoints)" opacity="0.5" />
  
  <!-- Decorative elements - data network lines -->
  <g opacity="0.3">
    <line x1="180" y1="240" x2="280" y2="190" stroke="#4B9CD3" stroke-width="1" />
    <line x1="180" y1="240" x2="220" y2="320" stroke="#4B9CD3" stroke-width="1" />
    <line x1="220" y1="320" x2="140" y2="380" stroke="#4B9CD3" stroke-width="1" />
    <line x1="220" y1="320" x2="320" y2="290" stroke="#4B9CD3" stroke-width="1" />
    <line x1="320" y1="290" x2="280" y2="190" stroke="#4B9CD3" stroke-width="1" />
    <line x1="140" y1="380" x2="240" y2="420" stroke="#4B9CD3" stroke-width="1" />
    
    <line x1="780" y1="740" x2="880" y2="690" stroke="#4B9CD3" stroke-width="1" />
    <line x1="780" y1="740" x2="820" y2="820" stroke="#4B9CD3" stroke-width="1" />
    <line x1="820" y1="820" x2="740" y2="880" stroke="#4B9CD3" stroke-width="1" />
    <line x1="820" y1="820" x2="920" y2="790" stroke="#4B9CD3" stroke-width="1" />
    <line x1="920" y1="790" x2="880" y2="690" stroke="#4B9CD3" stroke-width="1" />
    <line x1="740" y1="880" x2="840" y2="920" stroke="#4B9CD3" stroke-width="1" />
  </g>
  
  <!-- Browser bar -->
  <rect x="140" y="150" width="800" height="60" rx="10" ry="10" fill="#333333" />
  
  <!-- Browser buttons -->
  <circle cx="175" cy="180" r="8" fill="#FF605C" />
  <circle cx="205" cy="180" r="8" fill="#FFBD44" />
  <circle cx="235" cy="180" r="8" fill="#00CA4E" />
  
  <!-- URL bar -->
  <rect x="265" y="165" width="550" height="30" rx="15" ry="15" fill="#222222" />
  <text x="300" y="187" font-family="Arial, sans-serif" font-size="14" fill="#AAAAAA">https://datasci.daily/news/ai-updates</text>
  
  <!-- Refresh button -->
  <circle cx="845" cy="180" r="12" fill="transparent" stroke="#777777" stroke-width="2" />
  <path d="M845,174 L845,180 M845,180 L840,177" stroke="#777777" stroke-width="2" stroke-linecap="round" />
  
  <!-- Main content container -->
  <rect x="140" y="210" width="800" height="600" rx="6" ry="6" fill="rgba(30, 30, 30, 0.8)" />
  
  <!-- Hashtag pill -->
  <rect x="170" y="240" width="180" height="46" rx="23" ry="23" fill="#4B9CD3" />
  <text x="260" y="270" font-family="PingFang TC, Microsoft JhengHei, sans-serif" font-size="22" font-weight="600" fill="white" text-anchor="middle" id="hashtag">#人工智慧</text>
  
  <!-- Account name -->
  <text x="740" y="270" font-family="PingFang TC, Microsoft JhengHei, sans-serif" font-size="22" font-weight="500" fill="#CCCCCC" text-anchor="end" id="account">@datasci_daily</text>
  
  <!-- Main title -->
  <text x="540" y="450" font-family="PingFang TC, Microsoft JhengHei, sans-serif" font-size="66" font-weight="700" fill="#FFFFFF" text-anchor="middle" id="main-title">人工智慧最新發展</text>
  
  <!-- Subtitle -->
  <text x="540" y="520" font-family="PingFang TC, Microsoft JhengHei, sans-serif" font-size="30" font-weight="500" fill="#AAAAAA" text-anchor="middle" id="subtitle-1">最新技術突破與應用</text>
  <text x="540" y="570" font-family="PingFang TC, Microsoft JhengHei, sans-serif" font-size="30" font-weight="500" fill="#AAAAAA" text-anchor="middle" id="subtitle-2">深入解析與市場影響</text>
  
  <!-- Footer -->
  <text x="540" y="740" font-family="PingFang TC, Microsoft JhengHei, sans-serif" font-size="22" font-weight="500" fill="#AAAAAA" text-anchor="middle" id="footer">查看更多人工智慧新聞和分析</text>
  
  <!-- Arrow icon -->
  <circle cx="735" cy="740" r="18" fill="#4B9CD3" />
  <path d="M728,740 L742,740 M742,740 L735,733 M742,740 L735,747" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none" />
</svg>""")
            print(f"Created default cover template at {COVER_TEMPLATE_PATH}")

# Call the function to ensure templates exist
ensure_templates_exist()