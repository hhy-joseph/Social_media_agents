import re
import os

class ChatXAI:
    """Implementation of the ChatXAI model interface for dynamic content generation."""
    
    def __init__(self, model):
        self.model = model
        print(f"已初始化 ChatXAI 模型: {model}")
    
    def invoke(self, prompt):
        """
        Invoke the model with the given prompt to generate content.
        
        Args:
            prompt (str): Input prompt
            
        Returns:
            str: Model generated content
        """
        # In a real implementation, this would call the actual XAI model API
        # For this simulation, we'll dynamically generate content based on the prompt
        print(f"正在使用 {self.model} 生成內容...")
        
        # Generate dynamic AI news content
        return self._generate_ai_news_content(prompt)
    
    def _generate_ai_news_content(self, prompt):
        """Generate dynamic AI news content based on the prompt."""
        # Create dynamic content with the current date to ensure freshness
        from datetime import datetime
        import random
        
        current_date = datetime.now().strftime("%Y年%m月%d日")
        
        # Generate a random AI news topic
        ai_topics = [
            "生成式AI", "大型語言模型", "電腦視覺", "自然語言處理", 
            "機器學習", "神經網絡", "強化學習", "自動駕駛", 
            "人工智慧倫理", "AI晶片技術", "量子AI", "AI醫療應用"
        ]
        
        # Select a random topic
        topic = random.choice(ai_topics)
        
        # Generate a random AI news headline
        headlines = {
            "生成式AI": ["生成式AI技術新突破", "大型語言模型效能提升", "更精準的圖像生成技術", "新型內容生成模型發表"],
            "大型語言模型": ["GPT新版本發布", "開源大型語言模型成就", "提升語言模型效能新方法", "語言模型的記憶力突破"],
            "電腦視覺": ["AI視覺識別新技術", "實時影像分析進展", "3D物體識別突破", "視覺理解新演算法"],
            "自然語言處理": ["多語言翻譯新進展", "語意理解技術突破", "情感分析新方法", "文本摘要演算法創新"],
            "機器學習": ["高效機器學習框架發布", "自我監督學習新方法", "小樣本學習技術突破", "模型壓縮新技術"],
            "神經網絡": ["神經網絡架構創新", "神經網絡訓練時間大幅縮短", "低功耗神經網絡硬體", "類腦計算新進展"],
            "強化學習": ["強化學習新演算法", "多代理協作系統突破", "模擬環境訓練新方法", "決策優化技術進展"],
            "自動駕駛": ["自動駕駛感知技術提升", "無人車測試新里程碑", "自動駕駛安全標準更新", "自駕車法規發展"],
            "人工智慧倫理": ["AI倫理準則發布", "人工智慧透明度新標準", "減少AI偏見的方法", "人機協作倫理框架"],
            "AI晶片技術": ["AI專用晶片性能突破", "低能耗AI計算架構", "邊緣計算晶片創新", "神經網絡處理器新一代"],
            "量子AI": ["量子機器學習演算法突破", "量子AI加速技術", "量子神經網絡原型", "混合量子-經典AI系統"],
            "AI醫療應用": ["AI醫學影像診斷新進展", "AI藥物發現突破", "醫療輔助AI系統獲批", "AI輔助醫療決策系統"]
        }
        
        random_headline = random.choice(headlines.get(topic, ["人工智慧最新發展"]))
        
        # Generate a unique title every time
        title = f"# {random_headline}：{topic}領域重大進展"
        
        # Generate description and content dynamically
        description = f"{current_date}報導：{random_headline}正在改變{topic}領域的未來，展現了人工智慧技術的驚人潛力和實際應用價值。"
        
        # Generate 4-7 pages of content dynamically
        num_pages = random.randint(4, 7)
        content_pages = []
        
        for i in range(1, num_pages + 1):
            if i == 1:
                content_pages.append(f"## 技術突破\n\n{current_date}，{topic}領域迎來重大突破：{random_headline}。這項創新由頂尖AI研究團隊開發，結合了最新的演算法和計算架構，實現了前所未有的性能和準確度。")
            elif i == 2:
                content_pages.append(f"## 關鍵創新\n\n此項{topic}技術的核心創新包括：\n• 全新的模型架構設計\n• 優化的資料處理方法\n• 突破性的訓練演算法\n• 高效能的模型部署策略\n\n這些創新結合在一起，使得系統性能提升超過50%。")
            elif i == 3:
                content_pages.append(f"## 實際應用\n\n{random_headline}在多個領域已展現出巨大潛力：\n• 醫療保健：提高疾病診斷準確率\n• 金融服務：加強風險評估和預測\n• 製造業：優化生產流程和質量控制\n• 交通運輸：增強安全性和效率")
            elif i == 4:
                content_pages.append(f"## 專家觀點\n\n知名{topic}專家表示：「這項技術代表了AI領域的重大進步，不僅在理論上有突破，更重要的是解決了實際應用中的關鍵挑戰。它將為產業帶來變革性的影響，同時推動整個領域向前發展。」")
            elif i == 5:
                content_pages.append(f"## 市場影響\n\n分析師預測，{random_headline}將對全球市場產生深遠影響：\n• 相關技術公司股價上漲\n• 新創企業獲得更多投資機會\n• 產業競爭格局重塑\n• 加速數位轉型步伐")
            elif i == 6:
                content_pages.append(f"## 未來展望\n\n隨著{topic}技術的持續發展，預計未來將出現：\n• 更多元化的應用場景\n• 更高的模型效能和準確度\n• 更強的可解釋性和透明度\n• 更廣泛的產業整合和採用")
            elif i == 7:
                content_pages.append(f"## 結論與思考\n\n{random_headline}不僅展示了技術進步，也提醒我們思考AI發展的方向和影響。如何平衡創新與倫理、效率與安全、商業價值與社會責任，將是整個行業需要共同面對的課題。")
        
        # Format the complete response
        complete_response = f"{title}\n---\n{description}\n---\n" + "\n\n".join([f"Page {i+1}:\n{page}" for i, page in enumerate(content_pages)])
        
        return complete_response
        

class ContentAgent:
    """Agent responsible for generating AI news content in Traditional Chinese."""
    
    def __init__(self, model_name="grok-2-1212"):
        self.llm = ChatXAI(model=model_name)
        
        # Initialize title tracker
        from ..utils.title_tracker import TitleTracker
        self.title_tracker = TitleTracker()
        
        # Initialize prompt loader
        from ..utils.prompt_loader import PromptLoader
        self.prompt_loader = PromptLoader()
        
        # Setup prompt file paths
        self.prompts_dir = "instagram_poster/prompts"
        self.ai_news_prompt_path = os.path.join(self.prompts_dir, "ai_news_prompt.txt")
        
        # Create prompts directory if it doesn't exist
        os.makedirs(self.prompts_dir, exist_ok=True)
        
        # Create default prompt files if they don't exist
        self._ensure_default_prompts()
    
    def _ensure_default_prompts(self):
        """Ensure default prompt templates exist."""
        default_ai_news_prompt = """根據以下人工智慧新聞資訊：

{news_text}

請選擇其中一則特定且有趣的人工智慧新聞故事。若新聞源為英文，請將內容翻譯成繁體中文。

請避免使用以下已經發布過的標題：
{used_titles}

請創建：
1. 一個吸引人的封面標題，清楚說明此特定人工智慧新聞故事
2. 一段簡短、吸引人的描述，用於Instagram帖子
3. 詳細內容分為4-7個信息頁面（不多不少）

每一頁應該在前一頁的基礎上建立，創建一個關於這個單一人工智慧新聞故事的連貫敘述。
包括相關細節、背景、影響和觀點。使其易於閱讀、視覺上吸引人且富有資訊性。

務必使用繁體中文（臺灣或香港使用的字符），而非簡體中文。

請以這種格式輸出:
# [標題]
---
[描述]
---
Page 1:
[第1頁內容]

Page 2:
[第2頁內容]

... 依此類推 ..."""

        # Create AI news prompt file if it doesn't exist
        if not os.path.exists(self.ai_news_prompt_path):
            with open(self.ai_news_prompt_path, 'w', encoding='utf-8') as f:
                f.write(default_ai_news_prompt)
    
    def generate_ai_news_content(self, news_data):
        """
        Generate content based on AI news data in Traditional Chinese.
        
        Args:
            news_data (dict): News search results
            
        Returns:
            dict: Generated content including title, description, and content pages
        """
        # Extract key information from the news data
        news_text = news_data.get("results", "")
        
        # Get previously used titles to avoid
        used_titles = self.title_tracker.get_used_titles(content_type="ai_news")
        used_titles_text = "\n".join(used_titles) if used_titles else "無"
        
        # Load and format the prompt template
        prompt_template = self.prompt_loader.load_prompt(self.ai_news_prompt_path)
        prompt = self.prompt_loader.format_prompt(
            prompt_template,
            news_text=news_text,
            used_titles=used_titles_text
        )
        
        # Generate content
        response = self.llm.invoke(prompt)
        
        # Process the response to extract the parts
        title, description, content = self._parse_content(response)
        
        # Ensure we have between 4-7 pages
        if len(content) < 4:
            # Pad content to minimum 4 pages if needed
            for i in range(len(content), 4):
                content.append(f"關於{title}的更多資訊")
        elif len(content) > 7:
            # Trim to maximum 7 pages if needed
            content = content[:7]
        
        # Track the title used
        self.title_tracker.add_title(title, content_type="ai_news")
        
        return {
            "title": title,
            "description": description,
            "content": content,
            "source": "news",
            "content_type": "ai_news"
        }
    
    def _parse_content(self, response_text):
        """
        Parse the LLM response to extract title, description, and content pages.
        
        Args:
            response_text (str): Model response
            
        Returns:
            tuple: (title, description, content_pages)
        """
        # Add debug print
        print(f"Parsing response text of type: {type(response_text)}")
        
        if isinstance(response_text, str):
            text = response_text.strip()
        else:
            # Handle potential object with content attribute
            text = getattr(response_text, 'content', str(response_text)).strip()
        
        # Add debug print
        print(f"Response text first 100 chars: {text[:100]}")
        
        # Split by sections using the separator '---'
        sections = text.split("---")
        
        # Add debug print
        print(f"Found {len(sections)} sections after splitting by '---'")
        
        # Extract title (first section)
        title = sections[0].strip() if len(sections) > 0 else "未生成標題"
        title = title.replace('#', '').strip()  # Remove markdown heading symbols
        
        # Extract description (second section)
        description = sections[1].strip() if len(sections) > 1 else "未生成描述"
        
        # Extract content pages (third section)
        content_text = sections[2] if len(sections) > 2 else ""
        
        # Split content by "Page X:" pattern
        pages = re.split(r'Page \d+:', content_text)
        content_pages = [page.strip() for page in pages if page.strip()]
        
        # Add debug print
        print(f"Extracted title: {title}")
        print(f"Extracted {len(content_pages)} content pages")
        
        return title, description, content_pages