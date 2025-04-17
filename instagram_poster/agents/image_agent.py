import os
from xml.dom import minidom
import re
import textwrap

class ImageAgent:
    """Agent responsible for generating SVG files from templates."""
    
    def __init__(self, cover_template_path, content_template_path, output_dir):
        self.cover_template_path = cover_template_path
        self.content_template_path = content_template_path
        self.output_dir = output_dir
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_images(self, content_data):
        """
        Generate SVG files based on the provided content data.
        
        Args:
            content_data (dict): Content data including title and content pages
            
        Returns:
            dict: Paths to generated files
        """
        # Add debug logging
        print(f"Content data type: {type(content_data)}")
        print(f"Content data keys: {content_data.keys() if isinstance(content_data, dict) else 'Not a dictionary'}")
        
        # Safely extract title, description, and content
        if not isinstance(content_data, dict):
            print("WARNING: content_data is not a dictionary. Using default values.")
            title = "人工智慧最新發展"
            description = "最新技術突破與市場應用"
            content_pages = ["暫無內容"]
        else:
            title = content_data.get("title", "人工智慧最新發展")
            description = content_data.get("description", "最新技術突破與市場應用")
            content_pages = content_data.get("content", ["暫無內容"])
        
        # Generate cover SVG
        cover_svg_path = self._generate_cover_svg(title, description)
        
        # Generate content SVGs
        content_svg_paths = self._generate_content_svgs(content_pages)
        
        # To maintain backward compatibility with the workflow, we'll still use PNG extensions
        # in the paths, even though we're actually generating SVG files
        cover_image_path = cover_svg_path.replace('.svg', '.png')
        content_image_paths = [path.replace('.svg', '.png') for path in content_svg_paths]
        
        return {
            "cover_image": cover_image_path,
            "content_images": content_image_paths,
            "all_images": [cover_image_path] + content_image_paths
        }
    
    def _generate_cover_svg(self, title, description):
        """
        Generate cover SVG using the template.
        
        Args:
            title (str): Title to display on the cover
            description (str): Description for the cover
            
        Returns:
            str: Path to the generated SVG file
        """
        output_path = os.path.join(self.output_dir, "cover.svg")
        
        # Load the SVG template
        svg_content = self._load_svg_template(self.cover_template_path)
        
        # Process the template
        modified_svg = self._process_cover_template(svg_content, title, description)
        
        # Save the modified SVG
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(modified_svg)
        
        print(f"已生成封面 SVG 檔案: {output_path}")
        return output_path
    
    def _generate_content_svgs(self, content_pages):
        """
        Generate content SVGs for each page.
        
        Args:
            content_pages (list): List of content for each page
            
        Returns:
            list: Paths to the generated SVG files
        """
        output_paths = []
        
        for i, page_content in enumerate(content_pages):
            output_path = os.path.join(self.output_dir, f"content_{i+1}.svg")
            
            # Load the SVG template
            svg_content = self._load_svg_template(self.content_template_path)
            
            # Process the template - parse content to get title and paragraphs
            title, paragraphs = self._parse_page_content(page_content)
            modified_svg = self._process_content_template(svg_content, title, paragraphs)
            
            # Save the modified SVG
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(modified_svg)
            
            print(f"已生成內容 SVG 檔案: {output_path}")
            output_paths.append(output_path)
        
        return output_paths
    
    def _parse_page_content(self, content):
        """
        Parse page content to extract title and paragraphs.
        
        Args:
            content (str): Page content
            
        Returns:
            tuple: (title, paragraphs list)
        """
        # Split content by lines
        lines = content.strip().split('\n')
        
        # Extract title (assuming it starts with ##)
        title = ""
        paragraphs = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('##'):
                title = line.replace('##', '').strip()
            elif line and not line.startswith('#'):
                # Split into bullet points or regular paragraphs
                if '•' in line:
                    bullet_points = line.split('•')
                    for point in bullet_points:
                        if point.strip():
                            paragraphs.append('• ' + point.strip())
                else:
                    paragraphs.append(line)
        
        # If no title found, use first line as title
        if not title and paragraphs:
            title = paragraphs[0]
            paragraphs = paragraphs[1:]
        
        return title, paragraphs
    
    def _load_svg_template(self, template_path):
        """
        Load an SVG template from file.
        
        Args:
            template_path (str): Path to the SVG template
            
        Returns:
            str: SVG template content
        """
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def _truncate_text(self, text, max_length, add_ellipsis=True):
        """
        Truncate text to fit in SVG elements.
        
        Args:
            text (str): Text to truncate
            max_length (int): Maximum length
            add_ellipsis (bool): Whether to add ellipsis
            
        Returns:
            str: Truncated text
        """
        if len(text) <= max_length:
            return text
        
        return text[:max_length] + ('...' if add_ellipsis else '')
    
    def _process_cover_template(self, svg_content, title, description):
        """
        Process the cover template by inserting title and description.
        
        Args:
            svg_content (str): SVG template content
            title (str): Title to insert
            description (str): Description to insert
            
        Returns:
            str: Processed SVG content
        """
        # Remove markdown formatting from title if present
        title = title.replace('#', '').strip()
        
        # Parse SVG content
        doc = minidom.parseString(svg_content)
        
        # Update main title text node
        main_title_elements = doc.getElementsByTagName('text')
        for element in main_title_elements:
            if element.getAttribute('id') == 'main-title':
                # Clear existing content
                while element.firstChild:
                    element.removeChild(element.firstChild)
                
                # Create tspan element for the title with proper wrapping
                # Split title into two lines if it's too long
                if len(title) > 24:
                    # Create two lines with approximately equal length
                    words = title.split()
                    line1 = []
                    line2 = []
                    
                    # Distribute words between lines
                    current_line = line1
                    for word in words:
                        if len(' '.join(current_line + [word])) <= 24:
                            current_line.append(word)
                        else:
                            if current_line == line1:
                                current_line = line2
                                current_line.append(word)
                            else:
                                # If already on second line, just append and will truncate later
                                current_line.append(word)
                    
                    # Create first line tspan
                    tspan1 = doc.createElement('tspan')
                    tspan1.setAttribute('x', '540')  # Center align
                    tspan1.setAttribute('text-anchor', 'middle')  # Center align
                    line1_text = self._truncate_text(' '.join(line1), 24)
                    tspan1.appendChild(doc.createTextNode(line1_text))
                    element.appendChild(tspan1)
                    
                    # Create second line tspan
                    tspan2 = doc.createElement('tspan')
                    tspan2.setAttribute('x', '540')  # Center align
                    tspan2.setAttribute('dy', '80')  # Line spacing
                    tspan2.setAttribute('text-anchor', 'middle')  # Center align
                    line2_text = self._truncate_text(' '.join(line2), 24)
                    tspan2.appendChild(doc.createTextNode(line2_text))
                    element.appendChild(tspan2)
                else:
                    # Single line title
                    element.appendChild(doc.createTextNode(title))
            
            # Update subtitle with description
            elif element.getAttribute('id') == 'subtitle-1' or element.getAttribute('id') == 'subtitle-2':
                # Clear existing content
                while element.firstChild:
                    element.removeChild(element.firstChild)
                
                # Split description into two parts for two subtitle elements
                if len(description) > 0:
                    parts = textwrap.wrap(description, width=30)
                    
                    if element.getAttribute('id') == 'subtitle-1':
                        # First subtitle gets first part
                        element.appendChild(doc.createTextNode(parts[0] if parts else ''))
                    elif element.getAttribute('id') == 'subtitle-2' and len(parts) > 1:
                        # Second subtitle gets second part
                        element.appendChild(doc.createTextNode(parts[1]))
            
            # Update hashtag
            elif element.getAttribute('id') == 'hashtag':
                # Clear existing content
                while element.firstChild:
                    element.removeChild(element.firstChild)
                
                # Add AI hashtag
                element.appendChild(doc.createTextNode('#人工智慧'))
        
        return doc.toxml()
    
    def _process_content_template(self, svg_content, title, paragraphs):
        """
        Process the content template by inserting title and paragraphs.
        
        Args:
            svg_content (str): SVG template content
            title (str): Title to insert
            paragraphs (list): Paragraphs to insert
            
        Returns:
            str: Processed SVG content
        """
        # Parse SVG content
        doc = minidom.parseString(svg_content)
        
        # Update title
        title_elements = doc.getElementsByTagName('text')
        for element in title_elements:
            if element.getAttribute('id') == 'content-title':
                # Clear existing content
                while element.firstChild:
                    element.removeChild(element.firstChild)
                
                # Handle multi-line titles
                if len(title) > 20:
                    # Create two lines with approximately equal length
                    words = title.split()
                    line1 = []
                    line2 = []
                    
                    # Distribute words between lines
                    current_line = line1
                    for word in words:
                        if len(' '.join(current_line + [word])) <= 20:
                            current_line.append(word)
                        else:
                            if current_line == line1:
                                current_line = line2
                                current_line.append(word)
                            else:
                                # If already on second line, just append and will truncate later
                                current_line.append(word)
                    
                    # Create first line tspan
                    tspan1 = doc.createElement('tspan')
                    tspan1.setAttribute('x', '190')
                    line1_text = self._truncate_text(' '.join(line1), 20)
                    tspan1.appendChild(doc.createTextNode(line1_text))
                    element.appendChild(tspan1)
                    
                    # Create second line tspan
                    tspan2 = doc.createElement('tspan')
                    tspan2.setAttribute('x', '190')
                    tspan2.setAttribute('dy', '50')
                    line2_text = self._truncate_text(' '.join(line2), 20)
                    tspan2.appendChild(doc.createTextNode(line2_text))
                    element.appendChild(tspan2)
                else:
                    # Single line title
                    element.appendChild(doc.createTextNode(title))
        
        # Update paragraphs
        for i, para in enumerate(paragraphs[:7], 1):  # Limit to 7 paragraphs
            para_id = f"p{i}"
            for element in title_elements:
                if element.getAttribute('id') == para_id:
                    # Clear existing content
                    while element.firstChild:
                        element.removeChild(element.firstChild)
                    
                    # Create multiline paragraph if needed
                    if len(para) > 25:
                        parts = textwrap.wrap(para, width=25, break_long_words=False)
                        first_part = parts[0] if parts else ''
                        element.appendChild(doc.createTextNode(first_part + ('' if len(parts) <= 1 else '...')))
                    else:
                        element.appendChild(doc.createTextNode(para))
        
        # Update highlight text with a key point
        highlight_elements = doc.getElementsByTagName('text')
        for element in highlight_elements:
            if element.getAttribute('id') == 'highlight-text':
                # Clear existing content
                while element.firstChild:
                    element.removeChild(element.firstChild)
                
                # Add a key point from paragraphs if available
                if paragraphs and len(paragraphs) >= 2:
                    key_point = self._truncate_text(paragraphs[1].replace('• ', ''), 30)
                    element.appendChild(doc.createTextNode(key_point))
                else:
                    element.appendChild(doc.createTextNode("人工智慧的最新發展"))
        
        return doc.toxml()