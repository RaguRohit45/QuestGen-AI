import PyPDF2
import pdfplumber
import os

class PDFProcessor:
    """Class to handle PDF reading and text extraction"""
    
    def __init__(self):
        self.supported_formats = ['pdf']
    
    def extract_text(self, filepath):
        """
        Extract text from PDF file using multiple methods for better accuracy
        
        Args:
            filepath: Path to the PDF file
            
        Returns:
            str: Extracted text content
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        text_content = ""
        try:
            with pdfplumber.open(filepath) as pdf:
                pages_text = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        pages_text.append(page_text)
                text_content = "\n\n".join(pages_text)
                
                if text_content.strip():
                    return text_content
        except Exception as e:
            print(f"pdfplumber extraction failed: {e}")
        
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pages_text = []
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        pages_text.append(page_text)
                
                text_content = "\n\n".join(pages_text)
                
                if text_content.strip():
                    return text_content
        except Exception as e:
            print(f"PyPDF2 extraction failed: {e}")
        
        if not text_content.strip():
            raise ValueError(f"Could not extract text from PDF: {filepath}")
        
        return text_content
    
    def extract_metadata(self, filepath):
        """
        Extract metadata from PDF file
        
        Args:
            filepath: Path to the PDF file
            
        Returns:
            dict: PDF metadata
        """
        metadata = {}
        
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = {
                    'num_pages': len(pdf_reader.pages),
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'subject': pdf_reader.metadata.get('/Subject', ''),
                }
        except Exception as e:
            print(f"Metadata extraction failed: {e}")
        
        return metadata
    
    def split_text_into_chunks(self, text, chunk_size=1000, overlap=200):
        """
        Split text into chunks for processing
        
        Args:
            text: Text to split
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            list: List of text chunks
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks

