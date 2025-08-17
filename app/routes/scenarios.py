from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.query import ScenarioRequest, LegalQueryResponse
from app.services.ai_service import AIService
from app.database.models import Query, User
from app.routes.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
ai_service = AIService()

@router.get("/list")
async def get_scenarios():
    """Get list of available legal scenarios"""
    scenarios = {
        "landlord_dispute": {
            "title": "Landlord/Tenant Dispute",
            "description": "Issues with rent, eviction, property maintenance",
            "icon": "🏠"
        },
        "police_trouble": {
            "title": "Police/Legal Trouble",
            "description": "Arrest, detention, police questioning",
            "icon": "👮"
        },
        "money_recovery": {
            "title": "Money Recovery",
            "description": "Debt collection, loan disputes, unpaid dues",
            "icon": "💰"
        },
        "harassment": {
            "title": "Harassment Issues",
            "description": "Workplace, domestic, or cyber harassment",
            "icon": "🚫"
        },
        "property_dispute": {
            "title": "Property Disputes",
            "description": "Land disputes, property ownership issues",
            "icon": "📋"
        },
        "employment": {
            "title": "Employment Issues",
            "description": "Workplace rights, salary disputes, termination",
            "icon": "💼"
        },
        "family_law": {
            "title": "Family Law",
            "description": "Marriage, divorce, custody, inheritance",
            "icon": "👨‍👩‍👧‍👦"
        },
        "consumer_rights": {
            "title": "Consumer Rights",
            "description": "Product defects, service issues, refunds",
            "icon": "🛒"
        }
    }
    
    return {"scenarios": scenarios}

@router.post("/analyze", response_model=LegalQueryResponse)
async def analyze_scenario(
    request: ScenarioRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze a specific legal scenario"""
    try:
        ai_response = await ai_service.analyze_legal_scenario(
            scenario=request.description or "",
            scenario_type=request.scenario_type,
            language=request.language
        )
        
        # Save query to database
        db_query = Query(
            user_id=current_user.id,
            query_text=f"Scenario: {request.scenario_type} - {request.description}",
            response_text=ai_response["response"],
            query_type="scenario",
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
        logger.error(f"Error analyzing scenario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing your scenario."
        )