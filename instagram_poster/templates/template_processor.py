import re
from xml.dom import minidom

class TemplateProcessor:
    """Processes SVG templates by replacing placeholders with actual content."""
    
    @staticmethod
    def process_cover_template(svg_content, title):
        """
        Process the cover template by replacing title placeholder.
        
        Args:
            svg_content (str): SVG template content
            title (str): Title to insert
            
        Returns:
            str: Processed SVG content
        """
        # Parse the SVG as XML
        doc = minidom.parseString(svg_content)
        
        # Find text elements
        text_elements = doc.getElementsByTagName('text')
        
        # Look for the title element by id or content
        title_found = False
        for elem in text_elements:
            if (elem.getAttribute('id') == 'title' or 
                'TITLE_PLACEHOLDER' in elem.textContent):
                # Clear existing content
                while elem.firstChild:
                    elem.removeChild(elem.firstChild)
                
                # Add new title
                text_node = doc.createTextNode(title)
                elem.appendChild(text_node)
                title_found = True
                break
        
        # If no placeholder found, try simple string replacement as fallback
        if not title_found:
            return svg_content.replace('TITLE_PLACEHOLDER', title)
            
        return doc.toxml()
    
    @staticmethod
    def process_content_template(svg_content, content):
        """
        Process the content template by replacing content placeholder.
        
        Args:
            svg_content (str): SVG template content
            content (str): Content to insert
            
        Returns:
            str: Processed SVG content
        """
        # Parse the SVG as XML
        doc = minidom.parseString(svg_content)
        
        # Find text elements
        text_elements = doc.getElementsByTagName('text')
        
        # Look for the content element by id or content
        content_found = False
        for elem in text_elements:
            if (elem.getAttribute('id') == 'content' or 
                'CONTENT_PLACEHOLDER' in elem.textContent):
                # Clear existing content
                while elem.firstChild:
                    elem.removeChild(elem.firstChild)
                
                # Add new content
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if i > 0:
                        # Add a line break for multi-line content
                        elem.appendChild(doc.createElement('tspan'))
                    
                    tspan = doc.createElement('tspan')
                    tspan.setAttribute('x', '50')  # Set x position
                    tspan.setAttribute('dy', '1.2em' if i > 0 else '0')  # Set line spacing
                    tspan.appendChild(doc.createTextNode(line))
                    elem.appendChild(tspan)
                
                content_found = True
                break
        
        # If no placeholder found, try simple string replacement as fallback
        if not content_found:
            return svg_content.replace('CONTENT_PLACEHOLDER', content)
            
        return doc.toxml()