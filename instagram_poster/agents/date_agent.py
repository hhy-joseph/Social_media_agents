from instagram_poster.utils.date_utils import get_current_date

class DateAgent:
    """Agent responsible for determining content type based on the current date."""
    
    def determine_content_type(self):
        """
        Always returns AI news content type regardless of the day.
        
        Returns:
            dict: Information about the date and content type
        """
        current_date = get_current_date()
        
        # Chinese weekday names
        weekday_names = {
            0: "星期一",  # Monday
            1: "星期二",  # Tuesday
            2: "星期三",  # Wednesday
            3: "星期四",  # Thursday
            4: "星期五",  # Friday
            5: "星期六",  # Saturday
            6: "星期日"   # Sunday
        }
        
        weekday_num = current_date.weekday()
        weekday_chinese = weekday_names.get(weekday_num, "未知")
        
        # Now always return AI news regardless of day
        return {
            "content_type": "ai_news",
            "date": current_date,
            "weekday": current_date.strftime("%A"),
            "weekday_chinese": weekday_chinese,
            "message": f"今天是{weekday_chinese}，生成人工智慧新聞內容。"
        }