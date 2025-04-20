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
                # First try with specific DPI for higher quality
                subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', '-f', 'png', 
                              '-o', str(output_path), temp_svg.name], 
                              check=True, timeout=30)
                success = True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
                logger.warning(f"High-DPI rsvg-convert failed: {e}. Trying standard version...")
                try:
                    # Fallback to standard conversion
                    subprocess.run(['rsvg-convert', '-f', 'png', '-o', str(output_path), temp_svg.name], 
                                  check=True, timeout=30)
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
            
            # Write the PNG data to file
            with open(output_path, "wb") as f:
                f.write(png_data.getvalue())
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"Successfully converted SVG to PNG using CairoSVG (unsafe=True)")
                return True
                
        except Exception as e:
            logger.warning(f"CairoSVG conversion with unsafe=True failed: {e}. Trying standard CairoSVG...")
            
            try:
                # Try standard CairoSVG without unsafe
                logger.info(f"Attempting SVG conversion with standard CairoSVG for {description}...")
                cairosvg.svg2png(bytestring=svg_data.encode('utf-8'), write_to=output_path)
                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    logger.info(f"Successfully converted SVG to PNG using standard CairoSVG")
                    return True
            except Exception as e2:
                logger.warning(f"Standard CairoSVG failed: {e2}. Trying direct file conversion...")
                
                try:
                    # Final fallback - try again with cairosvg directly on file
                    logger.info(f"Falling back to direct CairoSVG file conversion for {description}...")
                    cairosvg.svg2png(url=str(svg_path), write_to=str(output_path))
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        logger.info(f"Successfully converted SVG to PNG using direct file CairoSVG")
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
        output_path = self.output_dir / "cover.png"
        
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
        output_path = self.output_dir / f"content_{page_number:02d}.png"
        
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
        
        # Add line breaks to main_point text
        main_point = page_data['main_point']
        
        # Detect if text contains Chinese/Japanese/Korean characters
        import re
        has_cjk = bool(re.search(r'[\u4e00-\u9fff\u3040-\u30ff\u3400-\u4dbf]', main_point))
        
        if has_cjk:
            # For CJK text, break by character count (each character is a word)
            chars_per_line = 15  # Reduced for better fit within container
            main_point_with_breaks = ""
            
            # Split text into characters and process
            for i, char in enumerate(main_point):
                if i > 0 and i % chars_per_line == 0:
                    main_point_with_breaks += "\n"
                main_point_with_breaks += char
        else:
            # For non-CJK text, break by word count
            words_per_line = 12  # Reduced for better fit within container
            main_point_with_breaks = ""
            words = main_point.split()
            current_line = ""
            word_count = 0
            
            for word in words:
                if word_count >= words_per_line:
                    main_point_with_breaks += current_line.strip() + "\n"
                    current_line = word + " "
                    word_count = 1
                else:
                    current_line += word + " "
                    word_count += 1
            
            main_point_with_breaks += current_line.strip()
        
        # Find the main_point foreignObject container to replace its content
        import re
        
        # Approach: Convert from using foreignObject (which many SVG renderers have issues with)
        # to using SVG native text elements for better compatibility
        
        # First check for foreignObject containing main_point
        foreign_object_pattern = r'<foreignObject[^>]*>(.*?)<div[^>]*id="main_point"[^>]*>.*?</div>(.*?)</foreignObject>'
        foreign_object_match = re.search(foreign_object_pattern, svg_content, re.DOTALL)
        
        if foreign_object_match:
            # Get the coordinates and dimensions of the foreignObject
            fo_coords = re.search(r'<foreignObject\s+x="(\d+)"\s+y="(\d+)"\s+width="(\d+)"\s+height="(\d+)"', svg_content)
            if fo_coords:
                x = int(fo_coords.group(1))
                y = int(fo_coords.group(2))
                width = int(fo_coords.group(3))
                height = int(fo_coords.group(4))
                
                # Remove the foreignObject completely
                svg_content = re.sub(foreign_object_pattern, '', svg_content, flags=re.DOTALL)
                
                # Create SVG native text elements instead
                lines = main_point_with_breaks.split('\n')
                line_height = 45  # Approximate line height
                
                # Generate text elements for each line
                text_elements = []
                base_y = y + 60  # Start y position with some margin from top
                
                for i, line in enumerate(lines):
                    # Sanitize line content to be safe in XML
                    safe_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    line_y = base_y + (i * line_height)
                    text_elements.append(f'<text x="{x + 30}" y="{line_y}" font-family="Songti SC, PingFang SC, Heiti SC, STKaiti, Kaiti SC, SimSong, Noto Sans CJK SC, Arial Unicode MS, Arial, sans-serif" font-weight="bold" font-size="38" fill="#000000">{safe_line}</text>')
                
                # Join all text elements and insert them after the containing rect
                rect_pattern = r'(<rect[^>]*x="{x}"[^>]*y="{y}"[^>]*width="{width}"[^>]*height="{height}"[^>]*/>|<rect[^>]*x="{x}"[^>]*y="{y}"[^>]*width="{width}"[^>]*height="{height}"[^>]*>)'
                rect_pattern = rect_pattern.format(x=x, y=y, width=width, height=height).replace('[^>]*', '.*?')
                
                # Insert text elements after the rectangle
                text_group = '\n  ' + '\n  '.join(text_elements)
                svg_content = re.sub(rect_pattern, r'\1' + text_group, svg_content, flags=re.DOTALL)
            else:
                # If we can't get the coordinates, create new rect and text elements
                # Place them in a sensible default position
                x, y = 200, 280
                
                # Create SVG native text elements
                lines = main_point_with_breaks.split('\n')
                line_height = 45  # Approximate line height
                
                # Generate text elements for each line
                text_elements = []
                base_y = y + 60  # Start y position with some margin from top
                
                for i, line in enumerate(lines):
                    # Sanitize line content to be safe in XML
                    safe_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    line_y = base_y + (i * line_height)
                    text_elements.append(f'<text x="{x + 30}" y="{line_y}" font-family="Songti SC, PingFang SC, Heiti SC, STKaiti, Kaiti SC, SimSong, Noto Sans CJK SC, Arial Unicode MS, Arial, sans-serif" font-weight="bold" font-size="38" fill="#000000">{safe_line}</text>')
                
                # Replace foreignObject with rect and text elements
                height = max(400, (len(lines) + 1) * line_height)
                replacement = f'<rect x="{x}" y="{y}" width="680" height="{height}" rx="20" ry="20" fill="#f0f0f0" stroke="#000000" stroke-width="1" />\n  ' + '\n  '.join(text_elements)
                svg_content = re.sub(foreign_object_pattern, replacement, svg_content, flags=re.DOTALL)
        
        
        else:
            # For backward compatibility - if the template uses the old text approach
            # First, look for a rect that might be the container for main_point
            rect_pattern = r'<rect[^>]*x="(\d+)"[^>]*y="(\d+)"[^>]*width="(\d+)"[^>]*height="(\d+)"[^>]*fill="#f0f0f0"[^>]*>'
            rect_match = re.search(rect_pattern, svg_content)
            
            # Default container dimensions if not found - from template inspection
            rect_x = 150  # Approximate x position of the container
            rect_y = 730  # Approximate y position of the container
            rect_width = 780  # Approximate width of the container
            rect_height = 150  # Approximate height of the container
            
            # If we found a container rect, use its dimensions
            if rect_match:
                rect_x = int(rect_match.group(1))
                rect_y = int(rect_match.group(2))
                rect_width = int(rect_match.group(3))
                rect_height = int(rect_match.group(4))
            
            # Split the content into lines
            lines = main_point_with_breaks.split('\n')
            line_height = 45  # Approximate line height
            
            # Generate text elements for each line
            text_elements = []
            base_y = rect_y + 60  # Start y position with some margin from top
            
            for i, line in enumerate(lines):
                # Sanitize line content to be safe in XML
                safe_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                line_y = base_y + (i * line_height)
                text_elements.append(f'<text x="{rect_x + 30}" y="{line_y}" font-family="Songti SC, PingFang SC, Heiti SC, STKaiti, Kaiti SC, SimSong, Noto Sans CJK SC, Arial Unicode MS, Arial, sans-serif" font-weight="bold" font-size="38" fill="#000000">{safe_line}</text>')
            
            # First, remove any existing main_point text element
            svg_content = re.sub(
                r'<text id="main_point"[^>]*>.*?</text>',
                '',
                svg_content,
                flags=re.DOTALL
            )
            
            # Then, add our new text elements after the container rectangle
            if rect_match:
                # Insert text elements after the rectangle
                rect_full_match = rect_match.group(0)
                text_group = '\n  ' + '\n  '.join(text_elements)
                svg_content = svg_content.replace(rect_full_match, rect_full_match + text_group)
            else:
                # If no rect was found, add both a rectangle and the text elements
                new_elements = f'''
  <rect x="{rect_x}" y="{rect_y}" width="{rect_width}" height="{rect_height}" rx="20" ry="20" fill="#f0f0f0" stroke="#000000" stroke-width="1" />
  {'\n  '.join(text_elements)}
'''
                # Insert before closing SVG tag
                svg_content = svg_content.replace('</svg>', new_elements + '\n</svg>')
            
        
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