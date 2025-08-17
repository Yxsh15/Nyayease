from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.query import LegalQueryRequest, LegalQueryResponse, ConstitutionQueryRequest, ScenarioRequest
from app.services.ai_service import AIService
from app.database.models import Query, User
from app.routes.auth import get_optional_current_user, get_current_user
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
ai_service = AIService()

@router.post("/ask", response_model=LegalQueryResponse)
async def ask_legal_question(
    request: LegalQueryRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """General legal query endpoint, now allows unauthenticated access"""
    try:
        document_context = None
        if request.document_id:
            document = db.query(Document).filter(Document.id == request.document_id).first()
            if not document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found."
                )
            # Ensure the document belongs to the current user if authenticated
            if current_user and document.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this document."
                )
            document_context = document.extracted_text

        # Get AI response
        ai_response = await ai_service.answer_legal_query(
            query=request.query,
            language=request.language,
            document_context=document_context # Pass document context to AI service
        )
        
        # Save query to database only if user is authenticated
        if current_user:
            db_query = Query(
                user_id=current_user.id,
                query_text=request.query,
                response_text=ai_response["response"],
                query_type=request.query_type,
                language=request.language
            )
            db.add(db_query)
            db.commit()
            
        return LegalQueryResponse(
            response=ai_response["response"],
            sources=ai_response["sources"],
            related_sections=ai_response.get("related_sections", []),
            confidence=ai_response["confidence"],
            language=request.language
        )
        
    except HTTPException as e:
        raise e # Re-raise HTTPExceptions directly
    except Exception as e:
        logger.error(f"Error processing legal query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing your query. Please try again."
        )

@router.post("/constitution", response_model=LegalQueryResponse)
async def ask_constitution(
    request: ConstitutionQueryRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Ask about Constitution articles and legal terms, now allows unauthenticated access"""
    try:
        ai_response = await ai_service.explain_constitution_article(
            article=request.article_or_term,
            language=request.language
        )
        
        # Save query to database only if user is authenticated
        if current_user:
            db_query = Query(
                user_id=current_user.id,
                query_text=f"Constitution: {request.article_or_term}",
                response_text=ai_response["response"],
                query_type="constitution",
                language=request.language
            )
            db.add(db_query)
            db.commit()
        
        return LegalQueryResponse(
            response=ai_response["response"],
            sources=ai_response["sources"],
            related_sections=ai_response.get("related_sections", []),
            confidence=ai_response["confidence"],
            language=request.language
        )
        
    except Exception as e:
        logger.error(f"Error processing constitution query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing your constitution query."
        )

@router.get("/history")
async def get_query_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's query history - This endpoint still requires authentication"""
    try:
        queries = db.query(Query).filter(
            Query.user_id == current_user.id
        ).order_by(Query.created_at.desc()).limit(20).all()
        
        return [
            {
                "id": query.id,
                "query_text": query.query_text,
                "response_text": query.response_text[:200] + "...",
                "query_type": query.query_type,
                "language": query.language,
                "created_at": query.created_at
            }
            for query in queries
        ]
        
    except Exception as e:
        logger.error(f"Error fetching query history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching query history."
        )
    