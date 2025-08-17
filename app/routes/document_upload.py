from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.document import DocumentResponse, DocumentAnalysisRequest
from app.services.ai_service import AIService
from app.services.ocr_service import OCRService
from app.services.vector_service import VectorService # Added this line
from app.database.models import Document, User
from app.routes.auth import get_current_user
from app.config import settings
import os
import uuid
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
ai_service = AIService()
ocr_service = OCRService()
vector_service = VectorService() # Added this line

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    language: Optional[str] = Form("en"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and analyze legal document"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check file size
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds limit"
            )
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File type not supported"
            )
        
        # Create unique filename
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = f"uploads/{unique_filename}"
        
        # Create uploads directory if not exists
        os.makedirs("uploads", exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Process and store the document in the vector database
        await vector_service.process_and_store_documents([file_path])
        
        # Extract text from document
        if file_ext == ".pdf":
            extracted_text = await ocr_service.extract_text_from_pdf(file_path)
        else:
            extracted_text = await ocr_service.extract_text_from_image(file_path)
        
        if not extracted_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from document"
            )
        
        # Analyze document using AI
        analysis_result = await ai_service.analyze_legal_document(
            document_text=extracted_text,
            language=language
        )
        
        # Save to database
        db_document = Document(
            user_id=current_user.id,
            filename=file.filename,
            file_path=file_path,
            extracted_text=extracted_text,
            analysis_result=str(analysis_result)
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        return DocumentResponse(
            id=db_document.id,
            filename=db_document.filename,
            extracted_text=extracted_text[:500] + "...",  # Truncate for response
            analysis_result=analysis_result["analysis"],
            upload_date=db_document.upload_date
        )
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        # Clean up file if it was created
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing document upload."
        )

@router.get("/list")
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's uploaded documents"""
    try:
        documents = db.query(Document).filter(
            Document.user_id == current_user.id
        ).order_by(Document.upload_date.desc()).all()
        
        return [
            {
                "id": doc.id,
                "filename": doc.filename,
                "upload_date": doc.upload_date,
                "analysis_preview": doc.analysis_result[:100] + "..."
            }
            for doc in documents
        ]
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching documents list."
        )

@router.get("/{document_id}")
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific document details"""
    try:
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return {
            "id": document.id,
            "filename": document.filename,
            "extracted_text": document.extracted_text,
            "analysis_result": document.analysis_result,
            "upload_date": document.upload_date
        }
        
    except Exception as e:
        logger.error(f"Error fetching document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching document details."
        )
@router.get("/{document_id}")
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific document details"""
    try:
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return {
            "id": document.id,
            "filename": document.filename,
            "extracted_text": document.extracted_text,
            "analysis_result": document.analysis_result,
            "upload_date": document.upload_date
        }
        
    except Exception as e:
        logger.error(f"Error fetching document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching document details."
        )

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific document"""
    try:
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Store file path before deletion
        file_path = document.file_path
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        # Delete physical file if it exists
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
            except OSError as e:
                logger.warning(f"Could not delete file {file_path}: {str(e)}")
        
        return {
            "message": "Document deleted successfully",
            "deleted_document": {
                "id": document.id,
                "filename": document.filename
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting document."
        )