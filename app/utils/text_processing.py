import re
from typing import List, Dict, Any
import string
from langchain.text_splitter import RecursiveCharacterTextSplitter

class TextProcessor:
    def __init__(self):
        self.legal_terms = {
            "constitution": ["article", "fundamental rights", "directive principles"],
            "ipc": ["section", "offence", "punishment", "imprisonment"],
            "crpc": ["procedure", "arrest", "bail", "investigation"],
            "civil": ["suit", "damages", "injunction", "contract"]
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep legal references
        text = re.sub(r'[^\w\s\.\,\;\:\(\)\-\/]', '', text)
        
        # Normalize legal references
        text = self._normalize_legal_references(text)
        
        return text.strip()
    
    def _normalize_legal_references(self, text: str) -> str:
        """Normalize legal references like Article 21, Section 498A"""
        # Normalize Article references
        text = re.sub(r'article\s*(\d+[a-z]*)', r'Article \1', text, flags=re.IGNORECASE)
        
        # Normalize Section references
        text = re.sub(r'section\s*(\d+[a-z]*)', r'Section \1', text, flags=re.IGNORECASE)
        
        # Normalize IPC references
        text = re.sub(r'ipc\s*(\d+[a-z]*)', r'IPC \1', text, flags=re.IGNORECASE)
        
        return text
    
    def extract_legal_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract legal entities from text"""
        entities = {
            "articles": [],
            "sections": [],
            "acts": [],
            "courts": []
        }
        
        # Extract Articles
        articles = re.findall(r'Article\s+(\d+[A-Z]*)', text, re.IGNORECASE)
        entities["articles"] = list(set(articles))
        
        # Extract Sections
        sections = re.findall(r'Section\s+(\d+[A-Z]*)', text, re.IGNORECASE)
        entities["sections"] = list(set(sections))
        
        # Extract Acts
        acts = re.findall(r'(\w+\s+Act,?\s*\d*)', text)
        entities["acts"] = list(set(acts))
        
        # Extract Court references
        courts = re.findall(r'(Supreme Court|High Court|District Court|Magistrate)', text, re.IGNORECASE)
        entities["courts"] = list(set(courts))
        
        return entities
    
    def chunk_legal_document(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split legal document into meaningful chunks"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", ".", "!", "?", ";", ",", " ", ""]
        )
        
        chunks = splitter.split_text(text)
        return chunks
    
    def detect_document_type(self, text: str) -> str:
        """Detect type of legal document"""
        text_lower = text.lower()
        
        type_indicators = {
            "constitution": ["fundamental rights", "directive principles", "amendment"],
            "ipc": ["indian penal code", "offence", "punishment"],
            "crpc": ["criminal procedure", "investigation", "trial"],
            "contract": ["agreement", "party", "consideration", "breach"],
            "notice": ["legal notice", "hereby", "whereas", "therefore"],
            "judgment": ["court", "judge", "order", "verdict", "judgment"]
        }
        
        scores = {}
        for doc_type, indicators in type_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            scores[doc_type] = score
        
        return max(scores, key=scores.get) if max(scores.values()) > 0 else "general"

