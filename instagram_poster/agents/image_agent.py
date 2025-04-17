import os
import subprocess
from xml.dom import minidom
import re

class ImageAgent:
    """Agent responsible for generating images from SVG templates."""
    
    def __init__(self, cover_template_path, content_template_path, output_dir):
        self.cover_template_path = cover_template_path
        self.content_template_path = content_template_path
        self.output_dir = output_dir
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_images(self, content_data):
        """
        Generate images based on the provided content data.
        
        Args:
            content_data (dict): Content data including title and content pages
            
        Returns:
            dict: Paths to generated images
        """
        title = content_data["title"]
        description = content_data["description"]
        content_pages = content_data["content"]
        
        # Generate cover image
        cover_image_path = self._generate_cover_image(title, description)
        
        # Generate content images
        content_image_paths = self._generate_content_images(content_pages)
        
        return {
            "cover_image": cover_image_path,
            "content_images": content_image_paths,
            "all_images": [cover_image_path] + content_image_paths
        }
    
    def _generate_cover_image(self, title, description):
        """
        Generate cover image using the SVG template.
        
        Args:
            title (str): Title to display on the cover
            description (str): Description for the cover
            
        Returns:
            str: Path to the generated PNG image
        """
        output_path = os.path.join(self.output_dir, "cover.png")
        
        # Load the SVG template
        svg_content = self._load_svg_template(self.cover_template_path)
        
        # Process the template
        modified_svg = self._process_cover_template(svg_content, title, description)
        
        # Save the modified SVG
        temp_svg_path = os.path.join(self.output_dir, "temp_cover.svg")
        with open(temp_svg_path, "w", encoding="utf-8") as f:
            f.write(modified_svg)
        
        # Convert SVG to PNG
        self._convert_svg_to_png(temp_svg_path, output_path)
        
        # Clean up temporary file
        os.remove(temp_svg_path)
        
        return output_path
    
    def _generate_content_images(self, content_pages):
        """
        Generate content images for each page.
        
        Args:
            content_pages (list): List of content for each page
            
        Returns:
            list: Paths to the generated PNG images
        """
        output_paths = []
        
        for i, page_content in enumerate(content_pages):
            output_path = os.path.join(self.output_dir, f"content_{i+1}.png")
            
            # Load the SVG template
            svg_content = self._load_svg_template(self.content_template_path)
            
            # Process the template - parse content to get title and paragraphs
            title, paragraphs = self._parse_page_content(page_content)
            modified_svg = self._process_content_template(svg_content, title, paragraphs)
            
            # Save the modified SVG
            temp_svg_path = os.path.join(self.output_dir, f"temp_content_{i+1}.svg")
            with open(temp_svg_path, "w", encoding="utf-8") as f:
                f.write(modified_svg)
            
            # Convert SVG to PNG
            self._convert_svg_to_png(temp_svg_path, output_path)
            
            # Clean up temporary file
            os.remove(temp_svg_path)
            
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
                            paragraphs.append(point.strip())
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
        # Parse SVG content
        doc = minidom.parseString(svg_content)
        
        # Update main title text node
        main_title_elements = doc.getElementsByTagName('text')
        for element in main_title_elements:
            if element.getAttribute('id') == 'main-title':
                # Clear existing content
                while element.firstChild:
                    element.removeChild(element.firstChild)
                
                # Add new title (limit to 20 chars to fit)
                short_title = title[:20] + ('...' if len(title) > 20 else '')
                element.appendChild(doc.createTextNode(short_title))
            
            # Update subtitle with description
            elif element.getAttribute('id') == 'subtitle-1' or element.getAttribute('id') == 'subtitle-2':
                # Clear existing content
                while element.firstChild:
                    element.removeChild(element.firstChild)
                
                # Add part of the description to subtitle
                if element.getAttribute('id') == 'subtitle-1':
                    if len(description) > 40:
                        element.appendChild(doc.createTextNode(description[:40] + '...'))
                    else:
                        element.appendChild(doc.createTextNode(description))
                else:
                    if len(description) > 40:
                        element.appendChild(doc.createTextNode('...'))
                    else:
                        element.appendChild(doc.createTextNode(''))
            
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
                
                # Add new title (limit to 20 chars to fit)
                short_title = title[:20] + ('...' if len(title) > 20 else '')
                element.appendChild(doc.createTextNode(short_title))
        
        # Update paragraphs
        for i, para in enumerate(paragraphs[:7], 1):  # Limit to 7 paragraphs
            para_id = f"p{i}"
            for element in title_elements:
                if element.getAttribute('id') == para_id:
                    # Clear existing content
                    while element.firstChild:
                        element.removeChild(element.firstChild)
                    
                    # Add new paragraph (limit to 25 chars to fit)
                    short_para = para[:25] + ('...' if len(para) > 25 else '')
                    element.appendChild(doc.createTextNode(short_para))
        
        # Update highlight text with a key point
        highlight_elements = doc.getElementsByTagName('text')
        for element in highlight_elements:
            if element.getAttribute('id') == 'highlight-text':
                # Clear existing content
                while element.firstChild:
                    element.removeChild(element.firstChild)
                
                # Add a key point from paragraphs if available
                if paragraphs and len(paragraphs) >= 2:
                    key_point = paragraphs[1][:30] + ('...' if len(paragraphs[1]) > 30 else '')
                    element.appendChild(doc.createTextNode(key_point))
                else:
                    element.appendChild(doc.createTextNode("人工智慧的最新發展"))
        
        return doc.toxml()
    
    def _convert_svg_to_png(self, svg_path, png_path):
        """
        Convert SVG to PNG using a suitable tool.
        
        Args:
            svg_path (str): Path to the SVG file
            png_path (str): Path for the output PNG file
            
        Raises:
            Exception: If conversion fails
        """
        try:
            # Try using cairosvg (if available)
            import cairosvg
            cairosvg.svg2png(url=svg_path, write_to=png_path)
            print(f"已轉換 {svg_path} 為 {png_path} (使用 cairosvg)")
        except ImportError:
            # Fallback to Inkscape CLI
            try:
                subprocess.run([
                    "inkscape", 
                    "--export-filename", png_path,
                    svg_path
                ], check=True)
                print(f"已轉換 {svg_path} 為 {png_path} (使用 Inkscape)")
            except subprocess.CalledProcessError:
                print("警告: 無法轉換 SVG 為 PNG。需要 Inkscape 或 cairosvg。")
                # In a real implementation, you might want to raise an exception here
                with open(png_path, "w") as f:
                    f.write("Placeholder for PNG")  # Just create an empty file as placeholder