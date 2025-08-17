import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import io
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        # Configure Tesseract for Indian languages
        self.ocr_config = r'--oem 3 --psm 6 -l eng+hin+mar'
    
    async def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF and OCR fallback"""
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Try direct text extraction first
                text = page.get_text()
                
                if len(text.strip()) < 50:  # Likely scanned PDF
                    # Use OCR on page image
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_data))
                    text = pytesseract.image_to_string(image, config=self.ocr_config)
                
                full_text += f"\n--- Page {page_num + 1} ---\n{text}"
            
            doc.close()
            return full_text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    async def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image file"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, config=self.ocr_config)
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return ""
