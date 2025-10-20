"""
PDF Text Extraction Module
Extracts text content from PDF files (resumes)
"""

import PyPDF2
from typing import Optional


class PDFExtractor:
    """Extract text from PDF files"""
    
    def __init__(self):
        pass
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            Exception: If there's an error reading the PDF
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                # Extract text from all pages
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
                
                return text.strip()
                
        except FileNotFoundError:
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_text_safe(self, pdf_path: str) -> Optional[str]:
        """
        Safely extract text from a PDF file, returning None on error
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as a string or None if extraction fails
        """
        try:
            return self.extract_text(pdf_path)
        except Exception as e:
            print(f"Warning: {str(e)}")
            return None
