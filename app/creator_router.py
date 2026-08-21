from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.models import User, CreatorProfile
from app.auth import get_current_user
from app.meta_api import fetch_recent_media_captions
from app.analyzer import InstagramAIAnalyzer

router = APIRouter(prefix="/creator", tags=["creator"])
templates = Jinja2Templates(directory="app/templates")
analyzer = InstagramAIAnalyzer()

@router.get("/dashboard", response_class=HTMLResponse)
async def creator_dashboard(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user or user.role != "creator":
        return RedirectResponse(url="/auth/login")

    profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == user.id).first()

    return templates.TemplateResponse(request, "creator.html", {
        "user": user,
        "profile": profile
    })

@router.post("/analyze")
async def trigger_ai_analysis(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user or user.role != "creator":
        raise HTTPException(status_code=403, detail="Unauthorized")

    profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == user.id).first()
    if not profile or not profile.meta_access_token:
        return RedirectResponse(url="/creator/dashboard")

    # Fetch recent captions to feed to AI
    captions = await fetch_recent_media_captions(profile.meta_access_token, profile.instagram_id)

    # Construct data object similar to what the analyzer expects
    profile_data = {
        "username": profile.instagram_username,
        "full_name": profile.full_name,
        "biography": profile.biography,
        "is_business_account": True,
        "business_category_name": profile.business_category,
        "recent_captions": captions
    }

    try:
        # Run AI Analysis
        analysis_result = analyzer.analyze_profile(profile_data)

        # Save to DB
        profile.ai_analysis = analysis_result
        db.commit()

    except Exception as e:
        return templates.TemplateResponse(request, "creator.html", {
            "user": user,
            "profile": profile,
            "error": f"AI Analysis failed: {str(e)}"
        })

    return RedirectResponse(url="/creator/dashboard", status_code=303)
