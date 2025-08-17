from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Document, User
from app.routes.auth import get_current_user, get_optional_current_user
from app.routes import auth, legal_query, document_upload, scenarios
from app.config import settings
import uvicorn

app = FastAPI(
    title="NyayEase - Legal AI Assistant",
    description="AI-powered legal assistant for Indian law",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates (now points to top-level "templates" folder)
templates = Jinja2Templates(directory="templates")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(legal_query.router, prefix="/api/v1/query", tags=["legal-query"])
app.include_router(document_upload.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(scenarios.router, prefix="/api/v1/scenarios", tags=["scenarios"])

@app.get("/")
async def home(request: Request, current_user: User | None = Depends(get_optional_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "current_user": current_user})

@app.get("/chat")
async def chat_page(request: Request, current_user: User | None = Depends(get_optional_current_user)):
    return templates.TemplateResponse("chat.html", {"request": request, "current_user": current_user})

@app.get("/documents")
async def documents_page(request: Request, current_user: User | None = Depends(get_optional_current_user)):
    return templates.TemplateResponse("documents.html", {"request": request, "current_user": current_user, "documents": []})

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
