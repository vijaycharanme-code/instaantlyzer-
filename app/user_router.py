from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import User, CreatorProfile
from app.auth import get_current_user

router = APIRouter(prefix="/user", tags=["user"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request, q: str = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user or user.role != "user":
        return RedirectResponse(url="/auth/login")

    # Query only creators who have connected their Instagram (have a meta_access_token)
    query = db.query(CreatorProfile).filter(CreatorProfile.meta_access_token.isnot(None))

    if q:
        # Search by username, full name, or within the AI analysis JSON blob
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                CreatorProfile.instagram_username.ilike(search_term),
                CreatorProfile.full_name.ilike(search_term),
                CreatorProfile.ai_analysis_json.ilike(search_term)
            )
        )

    creators = query.all()

    return templates.TemplateResponse(request, "user.html", {
        "user": user,
        "creators": creators,
        "query": q or ""
    })
