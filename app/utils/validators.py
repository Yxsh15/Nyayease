import re
from typing import Optional
from fastapi import HTTPException, status

class ValidationError(Exception):
    pass

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Za-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True

def validate_language_code(language: str) -> bool:
    """Validate language code"""
    supported_languages = ["en", "hi", "mr"]  # English, Hindi, Marathi
    return language in supported_languages

def validate_file_type(filename: str) -> bool:
    """Validate uploaded file type"""
    allowed_extensions = {'.pdf', '.txt', '.doc', '.docx', '.jpg', '.jpeg', '.png'}
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    return f'.{file_ext}' in allowed_extensions

def validate_query_length(query: str, max_length: int = 1000) -> bool:
    """Validate query length"""
    return len(query.strip()) > 0 and len(query) <= max_length