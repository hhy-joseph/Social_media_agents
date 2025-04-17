import re
from xml.dom import minidom
import textwrap

class TemplateProcessor:
    """Processes SVG templates by replacing placeholders with actual content."""
    
    @staticmethod
    def process_cover_template(svg_content, title, subtitle=None, hashtag=None):
        """
        Process the cover template by replacing title placeholder.
        
        Args:
            svg_content (str): SVG template content
            title (str): Title to insert
            subtitle (str, optional): Subtitle to insert
            hashtag (str, optional): Hashtag to insert
            
        Returns:
            str: Processed SVG content
        """
        # Parse the SVG as XML
        doc = minidom.parseString(svg_content)
        
        # Find text elements
        text_elements = doc.getElementsByTagName('text')
        
        # Remove any markdown from title
        title = title.replace('#', '').strip()
        
        # Process each text element
        for elem in text_elements:
            # Process main title
            if elem.getAttribute('id') == 'main-title':
                # Clear existing content
                while elem.firstChild:
                    elem.removeChild(elem.firstChild)
                
                # Handle long titles
                if len(title) > 24:
                    # Split title into multiple lines
                    title_lines = textwrap.wrap(title, width=24)
                    
                    # Create tspan for first line
                    first_line = doc.createElement('tspan')
                    first_line.setAttribute('x', '540')
                    first_line.setAttribute('text-anchor', 'middle')
                    first_line.appendChild(doc.createTextNode(title_lines[0]))
                    elem.appendChild(first_line)
                    
                    # Create tspan for second line if needed
                    if len(title_lines) > 1:
                        second_line = doc.createElement('tspan')
                        second_line.setAttribute('x', '540')
                        second_line.setAttribute('dy', '70')
                        second_line.setAttribute('text-anchor', 'middle')
                        second_line.appendChild(doc.createTextNode(title_lines[1]))
                        elem.appendChild(second_line)
                else:
                    # Add title directly
                    elem.appendChild(doc.createTextNode(title))
                
            # Process subtitle if provided
            elif (elem.getAttribute('id') == 'subtitle-1' or 
                  elem.getAttribute('id') == 'subtitle-2') and subtitle:
                
                # Clear existing content
                while elem.firstChild:
                    elem.removeChild(elem.firstChild)
                
                # Split subtitle into two parts
                subtitle_lines = textwrap.wrap(subtitle, width=35)
                
                # First subtitle element gets first line
                if elem.getAttribute('id') == 'subtitle-1' and subtitle_lines:
                    elem.appendChild(doc.createTextNode(subtitle_lines[0]))
                
                # Second subtitle element gets second line
                elif elem.getAttribute('id') == 'subtitle-2' and len(subtitle_lines) > 1:
                    elem.appendChild(doc.createTextNode(subtitle_lines[1]))
            
            # Process hashtag if provided
            elif elem.getAttribute('id') == 'hashtag' and hashtag:
                # Clear existing content
                while elem.firstChild:
                    elem.removeChild(elem.firstChild)
                
                # Add hashtag
                elem.appendChild(doc.createTextNode(hashtag))
        
        return doc.toxml()
    
    @staticmethod
    def process_content_template(svg_content, title, content_paragraphs):
        """
        Process the content template by replacing content placeholder.
        
        Args:
            svg_content (str): SVG template content
            title (str): Title to insert
            content_paragraphs (list): List of paragraphs to insert
            
        Returns:
            str: Processed SVG content
        """
        # Parse the SVG as XML
        doc = minidom.parseString(svg_content)
        
        # Find text elements
        text_elements = doc.getElementsByTagName('text')
        
        # Process title
        for elem in text_elements:
            if elem.getAttribute('id') == 'content-title':
                # Clear existing content
                while elem.firstChild:
                    elem.removeChild(elem.firstChild)
                
                # Handle long titles
                if len(title) > 20:
                    # Split into multiple lines
                    title_lines = textwrap.wrap(title, width=20)
                    
                    # Create tspan for first line
                    first_line = doc.createElement('tspan')
                    first_line.setAttribute('x', '190')
                    first_line.appendChild(doc.createTextNode(title_lines[0]))
                    elem.appendChild(first_line)
                    
                    # Create tspan for second line if needed
                    if len(title_lines) > 1:
                        second_line = doc.createElement('tspan')
                        second_line.setAttribute('x', '190')
                        second_line.setAttribute('dy', '50')
                        second_line.appendChild(doc.createTextNode(title_lines[1]))
                        elem.appendChild(second_line)
                else:
                    # Add title directly
                    elem.appendChild(doc.createTextNode(title))
        
        # Process paragraphs (up to 7)
        for i, para in enumerate(content_paragraphs[:7], 1):
            para_id = f"p{i}"
            
            for elem in text_elements:
                if elem.getAttribute('id') == para_id:
                    # Clear existing content
                    while elem.firstChild:
                        elem.removeChild(elem.firstChild)
                    
                    # Add paragraph text, truncating if needed
                    if len(para) > 25:
                        elem.appendChild(doc.createTextNode(para[:25] + "..."))
                    else:
                        elem.appendChild(doc.createTextNode(para))
        
        # Process highlight text (usually p2 or a key sentence)
        highlight_elem = None
        for elem in text_elements:
            if elem.getAttribute('id') == 'highlight-text':
                highlight_elem = elem
                break
        
        if highlight_elem and content_paragraphs:
            # Clear existing content
            while highlight_elem.firstChild:
                highlight_elem.removeChild(highlight_elem.firstChild)
            
            # Choose a good highlight (second paragraph or first if only one)
            highlight_text = content_paragraphs[1] if len(content_paragraphs) > 1 else content_paragraphs[0]
            
            # Truncate if needed
            if len(highlight_text) > 30:
                highlight_text = highlight_text[:30] + "..."
            
            # Remove bullet points if present
            highlight_text = highlight_text.replace('• ', '')
            
            highlight_elem.appendChild(doc.createTextNode(highlight_text))
        
        return doc.toxml()