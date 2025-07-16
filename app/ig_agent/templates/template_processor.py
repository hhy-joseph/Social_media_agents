"""
Template processor for SVG templates
"""

import os
import logging
import cairosvg
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("ig_agent.template_processor")

class TemplateProcessor:
    """
    Processor for SVG templates
    """
    
    def __init__(self, templates_dir=None, output_dir=None):
        """
        Initialize the TemplateProcessor
        
        Args:
            templates_dir: Directory containing SVG templates
            output_dir: Directory to save generated images
        """
        self.templates_dir = Path(templates_dir) if templates_dir else Path(__file__).parent.parent / "static"
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Template paths
        self.templates = {
            "cover": self.templates_dir / "cover.svg",
            "content_withimage": self.templates_dir / "content_withimage.svg",
            "content_withoutimage": self.templates_dir / "content_withoutimage.svg"
        }
        
        # Verify templates exist
        for name, path in self.templates.items():
            if not path.exists():
                logger.warning(f"Template not found: {path}")
                
        # Set default font for CairoSVG (if supported by your version)
        try:
            # Set multiple font-related environment variables for better Chinese support
            # Mac OS specific paths for Chinese fonts
            os.environ['PANGOCAIRO_FONT'] = 'PingFang SC,Heiti SC,Arial Unicode MS,SimSun,Noto Sans CJK SC,Arial'
            os.environ['FONTCONFIG_PATH'] = '/System/Library/Fonts:/Library/Fonts:/System/Library/Fonts/Supplemental:/usr/share/fonts'
            os.environ['PANGO_LANGUAGE'] = 'zh-CN,zh-TW,zh-HK'
            os.environ['LANG'] = 'zh_CN.UTF-8'
            os.environ['LC_ALL'] = 'zh_CN.UTF-8'
            
            # Use FC_DEBUG for font matching troubleshooting
            # Uncomment to debug font issues
            # os.environ['FC_DEBUG'] = '4'
            
            # Force CairoSVG to use system fonts
            try:
                import pycairo
                logger.info("PyCairo is available")
            except ImportError:
                logger.warning("PyCairo is not available, falling back to other methods")
                
            try:
                import cairosvg
                logger.info(f"CairoSVG version: {cairosvg.__version__}")
            except (ImportError, AttributeError):
                logger.warning("CairoSVG version info not available")
                
        except Exception as e:
            logger.warning(f"Could not set font environment variables: {e}")
    
    def _convert_png_to_jpg(self, png_path: str, jpg_path: str):
        """Convert PNG to JPG for Instagram compatibility"""
        try:
            from PIL import Image
            
            img = Image.open(png_path)
            # Convert to RGB mode if the image has an alpha channel
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # Save as JPG with high quality
            img.save(jpg_path, 'JPEG', quality=95)
            
            # Remove the PNG file
            os.remove(png_path)
            
            logger.info(f"Converted {png_path} to {jpg_path}")
            
        except Exception as e:
            logger.error(f"Failed to convert PNG to JPG: {e}")
            # If conversion fails, try to rename PNG to JPG
            try:
                os.rename(png_path, jpg_path)
            except:
                pass
            
    def _convert_svg_to_png(self, svg_data, svg_path, output_path, description=""):
        """
        Convert SVG to PNG using multiple methods
        
        Args:
            svg_data: SVG content as string
            svg_path: Path to SVG file
            output_path: Path to save PNG output
            description: Optional description for logging
            
        Returns:
            bool: True if conversion succeeded, False otherwise
        """
        # Method 1: Try using librsvg via rsvg-convert subprocess first (best support for SVG features)
        try:
            import subprocess
            import tempfile
            
            logger.info(f"Attempting SVG conversion with rsvg-convert for {description}...")
            
            # Create temporary file with correct encoding
            temp_svg = tempfile.NamedTemporaryFile(suffix='.svg', delete=False)
            temp_svg.write(svg_data.encode('utf-8'))
            temp_svg.close()
            
            try:
                # First try with specific DPI for higher quality - convert to JPG
                subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', '-f', 'png', 
                              '-o', str(output_path).replace('.jpg', '.png'), temp_svg.name], 
                              check=True, timeout=30)
                # Convert PNG to JPG
                self._convert_png_to_jpg(str(output_path).replace('.jpg', '.png'), str(output_path))
                success = True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
                logger.warning(f"High-DPI rsvg-convert failed: {e}. Trying standard version...")
                try:
                    # Fallback to standard conversion
                    subprocess.run(['rsvg-convert', '-f', 'png', '-o', str(output_path).replace('.jpg', '.png'), temp_svg.name], 
                                  check=True, timeout=30)
                    # Convert PNG to JPG
                    self._convert_png_to_jpg(str(output_path).replace('.jpg', '.png'), str(output_path))
                    success = True
                except Exception:
                    success = False
            
            # Clean up temp file
            os.unlink(temp_svg.name)
            
            if success:
                logger.info(f"Successfully converted SVG to PNG using rsvg-convert")
                return True
                
        except Exception as e:
            logger.warning(f"rsvg-convert method failed: {e}. Trying other methods...")
        
        # Method 2: Try Inkscape if available (excellent font handling)
        try:
            import subprocess
            
            logger.info(f"Attempting SVG conversion with Inkscape for {description}...")
            try:
                subprocess.run(['inkscape', '--export-filename', str(output_path), 
                               '--export-dpi', '300', svg_path], 
                               check=True, timeout=60)
                logger.info(f"Successfully converted SVG to PNG using Inkscape")
                return True
            except Exception as e:
                logger.warning(f"Inkscape conversion failed: {e}. Trying CairoSVG...")
        except Exception:
            pass
            
        # Method 3: Use CairoSVG with explicit UTF-8 encoding and unsafe option
        try:
            logger.info(f"Attempting SVG conversion with CairoSVG (unsafe=True) for {description}...")
            
            # Try with unsafe option first for better feature support
            import io
            png_data = io.BytesIO()
            cairosvg.svg2png(bytestring=svg_data.encode('utf-8'), 
                             write_to=png_data, 
                             unsafe=True)
            
            # Write the PNG data to temporary file, then convert to JPG
            temp_png = str(output_path).replace('.jpg', '.png')
            with open(temp_png, "wb") as f:
                f.write(png_data.getvalue())
            
            if os.path.exists(temp_png) and os.path.getsize(temp_png) > 0:
                # Convert to JPG
                self._convert_png_to_jpg(temp_png, str(output_path))
                logger.info(f"Successfully converted SVG to JPG using CairoSVG (unsafe=True)")
                return True
                
        except Exception as e:
            logger.warning(f"CairoSVG conversion with unsafe=True failed: {e}. Trying standard CairoSVG...")
            
            try:
                # Try standard CairoSVG without unsafe
                logger.info(f"Attempting SVG conversion with standard CairoSVG for {description}...")
                temp_png = str(output_path).replace('.jpg', '.png')
                cairosvg.svg2png(bytestring=svg_data.encode('utf-8'), write_to=temp_png)
                
                if os.path.exists(temp_png) and os.path.getsize(temp_png) > 0:
                    # Convert to JPG
                    self._convert_png_to_jpg(temp_png, str(output_path))
                    logger.info(f"Successfully converted SVG to JPG using standard CairoSVG")
                    return True
            except Exception as e2:
                logger.warning(f"Standard CairoSVG failed: {e2}. Trying direct file conversion...")
                
                try:
                    # Final fallback - try again with cairosvg directly on file
                    logger.info(f"Falling back to direct CairoSVG file conversion for {description}...")
                    temp_png = str(output_path).replace('.jpg', '.png')
                    cairosvg.svg2png(url=str(svg_path), write_to=temp_png)
                    
                    if os.path.exists(temp_png) and os.path.getsize(temp_png) > 0:
                        # Convert to JPG
                        self._convert_png_to_jpg(temp_png, str(output_path))
                        logger.info(f"Successfully converted SVG to JPG using direct file CairoSVG")
                        return True
                except Exception as e3:
                    logger.error(f"All CairoSVG methods failed. Last error: {e3}")
        
        # If we get here, all methods failed
        logger.error(f"All SVG conversion methods failed for {description}.")
        
        # Create a simple error image as fallback
        try:
            from PIL import Image, ImageDraw
            
            logger.info(f"Creating error fallback image for {description}...")
            img = Image.new('RGB', (1080, 1080), color='white')
            draw = ImageDraw.Draw(img)
            
            # Add error text
            draw.text((100, 500), f"Error converting SVG to PNG\n{description}", fill='black')
            img.save(output_path)
            
            logger.info(f"Created fallback error image")
            return True
        except Exception as e4:
            logger.error(f"Failed to create error image: {e4}")
            # Create an empty file to prevent further errors
            with open(output_path, 'wb') as f:
                f.write(b'')
            return False
    
    def generate_cover(self, cover_data: Dict[str, Any]) -> Path:
        """
        Generate cover image from template
        
        Args:
            cover_data: Cover data from content agent
            
        Returns:
            Path to generated image
        """
        output_path = self.output_dir / "cover.jpg"
        
        if not self.templates["cover"].exists():
            raise FileNotFoundError(f"Cover template not found: {self.templates['cover']}")
        
        with open(self.templates["cover"], "r", encoding="utf-8") as f:
            svg_content = f.read()
        
        # Replace template placeholders with content
        svg_content = svg_content.replace("#{Hashtag}", f"#{cover_data['hashtag']}")
        
        # Handle Chinese text properly - replace full-text elements rather than just placeholder text
        # For heading line 1 (top line)
        if 'heading_line1' in cover_data:
            heading_line1 = cover_data['heading_line1']
            svg_content = self._replace_text_element(svg_content, "heading_line1", heading_line1)
        
        # For heading line 2 (bottom line)
        if 'heading_line2' in cover_data:
            heading_line2 = cover_data['heading_line2']
            svg_content = self._replace_text_element(svg_content, "heading_line2", heading_line2)
        
        # For grey box text
        if 'grey_box_text' in cover_data:
            grey_box_text = cover_data['grey_box_text']
            svg_content = self._replace_text_element(svg_content, "grey_box_text", grey_box_text)
        
        # Write temporary SVG
        temp_svg_path = self.output_dir / "cover.svg"
        
        # Ensure all text elements have proper font-family for Chinese characters
        svg_content = self._ensure_chinese_font_support(svg_content)
        
        # Write the updated SVG with explicit UTF-8 encoding
        with open(temp_svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        # Read SVG content
        with open(temp_svg_path, "r", encoding="utf-8") as f:
            svg_data = f.read()
        
        # Use our helper method to convert SVG to PNG
        self._convert_svg_to_png(svg_data, temp_svg_path, output_path, description="cover")
            
        logger.info(f"Generated cover image: {output_path}")
        
        return output_path
        
    def _replace_text_element(self, svg_content: str, element_id: str, new_text: str) -> str:
        """
        Replace text in an SVG element by ID
        
        Args:
            svg_content: The SVG content as a string
            element_id: The ID of the element to replace
            new_text: The new text content
            
        Returns:
            Updated SVG content
        """
        import re
        # Look for a text element with the specified ID using regex
        pattern = rf'(<text[^>]*id="{element_id}"[^>]*>)(.*?)(</text>)'
        match = re.search(pattern, svg_content, re.DOTALL)
        
        if match:
            # Replace the font-family attribute to include Chinese fonts
            opening_tag = match.group(1)
            if "font-family" in opening_tag:
                # Add Chinese fonts to the font-family list
                opening_tag = re.sub(
                    r'font-family="([^"]*)"', 
                    r'font-family="Songti SC, PingFang SC, Heiti SC, STKaiti, Kaiti SC, SimSong, Noto Sans CJK SC, Arial Unicode MS, \1"', 
                    opening_tag
                )
            
            # Replace only the content between the opening and closing tags
            return svg_content.replace(match.group(0), f"{opening_tag}{new_text}{match.group(3)}")
        else:
            # If no match found, try simple text replacement as fallback
            # This is less precise but may work with simpler templates
            if element_id == "heading_line1":
                svg_content = svg_content.replace("人工智能如何", new_text)
            elif element_id == "heading_line2":
                svg_content = svg_content.replace("改變數據分析？", new_text)
            elif element_id == "grey_box_text":
                svg_content = svg_content.replace("掌握AI驅動的數據革命！", new_text)
            
            return svg_content
    
    def generate_content_page(self, page_data: Dict[str, Any], page_number: int, with_image: bool = True) -> Path:
        """
        Generate content page image from template
        
        Args:
            page_data: Page data from content agent
            page_number: Page number
            with_image: Whether to use template with image area
            
        Returns:
            Path to generated image
        """
        output_path = self.output_dir / f"content_{page_number:02d}.jpg"
        
        # Choose template based on whether we want image area
        template_name = "content_withimage" if with_image else "content_withoutimage"
        
        if not self.templates[template_name].exists():
            raise FileNotFoundError(f"Template not found: {self.templates[template_name]}")
        
        with open(self.templates[template_name], "r", encoding="utf-8") as f:
            svg_content = f.read()
        
        # Replace template placeholders with content
        svg_content = svg_content.replace("0{page_number}", f"{page_number:02d}")
        
        # Use text element replacement for title to ensure Chinese font support
        svg_content = self._replace_text_element(svg_content, "content_title", page_data['title'])
        
        # Get main_point text without manual line breaks - let CSS handle wrapping
        main_point = page_data['main_point']
        
        # Replace the main_point placeholder in the foreignObject
        svg_content = svg_content.replace(
            '<div id="main_point">核心訊息放這裡（最多50字）</div>',
            f'<div id="main_point">{main_point}</div>'
        )
        
        # Write temporary SVG
        temp_svg_path = self.output_dir / f"content_{page_number:02d}.svg"
        
        # Ensure all text elements have proper font-family for Chinese characters
        svg_content = self._ensure_chinese_font_support(svg_content)
        
        # Write the updated SVG with explicit UTF-8 encoding
        with open(temp_svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        # Read SVG content
        with open(temp_svg_path, "r", encoding="utf-8") as f:
            svg_data = f.read()
        
        # Use our helper method to convert SVG to PNG
        self._convert_svg_to_png(svg_data, temp_svg_path, output_path, description=f"content page {page_number}")
            
        logger.info(f"Generated content image {page_number}: {output_path}")
        
        return output_path
        
    def _create_multiline_text(self, text_id: str, x: int, y: int, text: str, font_size: int, line_height: int, align="left", margin=40) -> str:
        """
        Create SVG multiline text element
        
        Args:
            text_id: ID for the text element
            x: X coordinate
            y: Y coordinate
            text: Text content with line breaks
            font_size: Font size
            line_height: Line height
            align: Text alignment ("left", "center", or "right")
            margin: Margin to use for left or right alignment
            
        Returns:
            SVG text element with tspan elements for line breaks
        """
        lines = text.split("\n")
        
        # Adjust font size if there are too many lines to fit
        max_lines_before_resize = 5
        if len(lines) > max_lines_before_resize:
            # Scale down font size based on number of lines
            scale_factor = max(0.7, max_lines_before_resize / len(lines))
            adjusted_font_size = int(font_size * scale_factor)
            adjusted_line_height = int(line_height * scale_factor)
        else:
            adjusted_font_size = font_size
            adjusted_line_height = line_height
        
        # Calculate total height of text block for vertical centering
        total_height = adjusted_line_height * (len(lines) - 1)
        start_y = y - (total_height / 2)
        
        # Determine text-anchor based on alignment
        if align == "left":
            text_anchor = "start"
            # For left alignment, place text at the left edge of the container plus margin
            text_x = x - 360 + margin  # 360 is approximately half the width of the container (780/2)
        elif align == "right":
            text_anchor = "end"
            text_x = x + 350 - margin  # 350 is approximately half the width of the container
        else:  # center
            text_anchor = "middle"
            text_x = x
        
        # Use Chinese fonts first in the font-family list for better Chinese character support
        text_element = f'<text id="{text_id}" x="{text_x}" font-family="Songti SC, PingFang SC, Heiti SC, STKaiti, Kaiti SC, SimSong, Noto Sans CJK SC, Arial Unicode MS, Arial, sans-serif" font-weight="bold" font-size="{adjusted_font_size}" text-anchor="{text_anchor}" fill="#000000">'
        
        for i, line in enumerate(lines):
            line_y = start_y + (i * adjusted_line_height)
            text_element += f'<tspan x="{text_x}" y="{line_y}">{line}</tspan>'
        
        text_element += '</text>'
        return text_element
        
    def _ensure_chinese_font_support(self, svg_content: str) -> str:
        """
        Process SVG to ensure all text elements have font-family with Chinese support
        
        Args:
            svg_content: The SVG content as a string
            
        Returns:
            Updated SVG content with proper font-family attributes
        """
        import re
        
        # Ensure the SVG has proper XML declaration with UTF-8 encoding
        if not svg_content.startswith('<?xml'):
            svg_content = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + svg_content
        elif 'encoding=' not in svg_content.split('\n')[0]:
            # Replace existing XML declaration with one that includes UTF-8 encoding
            svg_content = re.sub(
                r'<\?xml[^>]*\?>', 
                '<?xml version="1.0" encoding="UTF-8" standalone="no"?>', 
                svg_content
            )
            
        # Add embedded font definition if svg element exists
        if '<svg' in svg_content and '<style' not in svg_content:
            # Create style element with embedded font definitions
            font_style = """
<style type="text/css">
@font-face {
  font-family: 'Songti SC';
  src: local('Songti SC');
  font-weight: normal;
  font-style: normal;
}
@font-face {
  font-family: 'PingFang SC';
  src: local('PingFang SC');
  font-weight: normal;
  font-style: normal;
}
@font-face {
  font-family: 'Heiti SC';
  src: local('Heiti SC');
  font-weight: normal;
  font-style: normal;
}
@font-face {
  font-family: 'Kaiti SC';
  src: local('Kaiti SC');
  font-weight: normal;
  font-style: normal;
}
</style>
"""
            # Insert style element after SVG opening tag
            svg_content = re.sub(r'(<svg[^>]*>)', r'\1' + font_style, svg_content)
        
        # Find all text elements that have a font-family attribute
        pattern = r'(<text[^>]*font-family="([^"]*)"[^>]*>)'
        matches = re.finditer(pattern, svg_content)
        
        # Replace each font-family attribute to include Chinese fonts
        for match in matches:
            full_tag = match.group(1)
            # Only replace if Chinese fonts aren't already included
            if not any(font in full_tag for font in ['PingFang', 'Heiti', 'Noto Sans CJK', 'Arial Unicode']):
                # Add Chinese fonts to the beginning of the font list
                new_tag = re.sub(
                    r'font-family="([^"]*)"', 
                    r'font-family="Songti SC, PingFang SC, Heiti SC, STKaiti, Kaiti SC, SimSong, Noto Sans CJK SC, Arial Unicode MS, \1"', 
                    full_tag
                )
                svg_content = svg_content.replace(full_tag, new_tag)
        
        # Find all text elements that don't have a font-family attribute and add one
        pattern = r'(<text[^>]*)(>)'
        matches = re.finditer(pattern, svg_content)
        
        for match in matches:
            full_tag = match.group(0)
            # Only process tags that don't already have font-family
            if 'font-family' not in full_tag:
                start_tag = match.group(1)
                end_bracket = match.group(2)
                # Add font-family attribute
                new_tag = f'{start_tag} font-family="Songti SC, PingFang SC, Heiti SC, STKaiti, Kaiti SC, SimSong, Noto Sans CJK SC, Arial Unicode MS, Arial, sans-serif"{end_bracket}'
                svg_content = svg_content.replace(full_tag, new_tag)
        
        return svg_content
    
    def _split_text_for_svg(self, text: str, max_chars_per_line: int = 16) -> list:
        """
        Split text into lines suitable for SVG rendering
        
        Args:
            text: Text to split
            max_chars_per_line: Maximum characters per line
            
        Returns:
            List of text lines
        """
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            # Check if adding this word would exceed the line limit
            test_line = current_line + " " + word if current_line else word
            
            if len(test_line) <= max_chars_per_line:
                current_line = test_line
            else:
                # If current line is not empty, save it and start new line
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Word is too long, split it
                    while len(word) > max_chars_per_line:
                        lines.append(word[:max_chars_per_line])
                        word = word[max_chars_per_line:]
                    current_line = word
        
        # Add the last line if it's not empty
        if current_line:
            lines.append(current_line)
            
        return lines
    
    def _create_svg_text_block(self, text_lines: list, x: int, y: int, font_size: int, 
                              line_height: int, max_width: int, fill: str = "#1d1d1f") -> str:
        """
        Create SVG text block with multiple lines
        
        Args:
            text_lines: List of text lines
            x: X position (center)
            y: Y position (center of text block)
            font_size: Font size
            line_height: Line height
            max_width: Maximum width for text
            fill: Text color
            
        Returns:
            SVG text element string
        """
        # Calculate starting Y position for vertical centering
        total_height = len(text_lines) * line_height
        start_y = y - (total_height / 2) + (line_height / 2)
        
        # Create the text element
        svg_text = f'''<text x="{x}" font-family="Songti SC, PingFang SC, Heiti SC, STKaiti, Kaiti SC, SimSong, Noto Sans CJK SC, Arial Unicode MS, Helvetica, Arial, sans-serif" font-weight="600" font-size="{font_size}" text-anchor="middle" fill="{fill}">'''
        
        for i, line in enumerate(text_lines):
            line_y = start_y + (i * line_height)
            svg_text += f'\n    <tspan x="{x}" y="{line_y}">{line}</tspan>'
        
        svg_text += '\n  </text>'
        
        return svg_text