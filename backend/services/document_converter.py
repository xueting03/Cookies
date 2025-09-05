"""
Document conversion service for converting markdown files to Word format only.
PDF conversion removed due to dependency issues.
"""

import os
from docx import Document
from docx.shared import Inches
import re
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentConverter:
    """Service for converting markdown documents to Word format only."""
    
    def __init__(self):
        """Initialize the document converter for Word documents only."""
        logger.info("DocumentConverter initialized for Word conversion only")
    
    def convert_to_word(self, markdown_file_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert markdown file to Word document.
        
        Args:
            markdown_file_path: Path to the markdown file
            output_path: Optional output path for Word doc. If None, uses same name with .docx extension
            
        Returns:
            Path to the generated Word document
        """
        try:
            # Read markdown content
            with open(markdown_file_path, 'r', encoding='utf-8') as file:
                markdown_content = file.read()
            
            # Determine output path
            if output_path is None:
                base_name = os.path.splitext(markdown_file_path)[0]
                output_path = f"{base_name}.docx"
            
            # Create Word document
            doc = Document()
            
            # Parse markdown and convert to Word elements
            lines = markdown_content.split('\n')
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    # Add paragraph break for empty lines
                    doc.add_paragraph()
                    continue
                
                # Handle headers
                if line.startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    header_text = line.lstrip('# ').strip()
                    
                    if level == 1:
                        doc.add_heading(header_text, level=1)
                    elif level == 2:
                        doc.add_heading(header_text, level=2)
                    elif level == 3:
                        doc.add_heading(header_text, level=3)
                    else:
                        doc.add_heading(header_text, level=4)
                
                # Handle code blocks
                elif line.startswith('```'):
                    # Skip code block markers for now
                    continue
                
                # Handle bullet points
                elif line.startswith('- ') or line.startswith('* '):
                    bullet_text = line[2:].strip()
                    doc.add_paragraph(bullet_text, style='List Bullet')
                
                # Handle numbered lists
                elif re.match(r'^\d+\.\s', line):
                    numbered_text = re.sub(r'^\d+\.\s', '', line)
                    doc.add_paragraph(numbered_text, style='List Number')
                
                # Regular paragraphs
                else:
                    # Handle inline code and formatting
                    clean_text = self._clean_markdown_formatting(line)
                    if clean_text:
                        doc.add_paragraph(clean_text)
            
            # Save document
            doc.save(output_path)
            logger.info(f"Word document generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting to Word: {str(e)}")
            raise
    
    def _clean_markdown_formatting(self, text: str) -> str:
        """Remove basic markdown formatting for Word conversion."""
        # Remove inline code backticks
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove bold/italic markers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        
        # Remove links (keep text only)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        return text
    
    def convert_documentation_folder(self, folder_path: str, formats: list = ['docx']) -> dict:
        """
        Convert all markdown files in a folder to Word format only.
        
        Args:
            folder_path: Path to folder containing markdown files
            formats: List of formats to convert to (only 'docx' supported)
            
        Returns:
            Dictionary with conversion results
        """
        results = {
            'converted': [],
            'errors': []
        }
        
        if not os.path.exists(folder_path):
            results['errors'].append(f"Folder not found: {folder_path}")
            return results
        
        # Find all markdown files
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.md'):
                    md_path = os.path.join(root, file)
                    
                    try:
                        if 'docx' in formats:
                            docx_path = self.convert_to_word(md_path)
                            results['converted'].append({
                                'source': md_path,
                                'output': docx_path,
                                'format': 'docx'
                            })
                        
                        # Skip PDF conversion - not supported
                        if 'pdf' in formats:
                            results['errors'].append({
                                'file': md_path,
                                'error': 'PDF conversion not available - feature removed'
                            })
                            
                    except Exception as e:
                        results['errors'].append({
                            'file': md_path,
                            'error': str(e)
                        })
        
        return results
