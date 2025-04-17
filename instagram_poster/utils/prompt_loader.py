import os

class PromptLoader:
    """Utility for loading prompt templates from files."""
    
    @staticmethod
    def load_prompt(prompt_file_path):
        """
        Load a prompt template from a file.
        
        Args:
            prompt_file_path (str): Path to the prompt template file
            
        Returns:
            str: The prompt template text
        """
        try:
            if not os.path.exists(prompt_file_path):
                return None
                
            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"載入提示模板時出錯: {e}")
            return None
    
    @staticmethod
    def format_prompt(prompt_template, **kwargs):
        """
        Format a prompt template with the given keyword arguments.
        
        Args:
            prompt_template (str): The prompt template
            **kwargs: Keyword arguments to insert into the template
            
        Returns:
            str: The formatted prompt
        """
        if not prompt_template:
            return ""
            
        try:
            return prompt_template.format(**kwargs)
        except KeyError as e:
            print(f"格式化提示模板時缺少關鍵字: {e}")
            return prompt_template
        except Exception as e:
            print(f"格式化提示模板時出錯: {e}")
            return prompt_template