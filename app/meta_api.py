import os
import httpx
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.database import get_db
from app.models import User, CreatorProfile
from app.auth import get_current_user

router = APIRouter(prefix="/meta", tags=["meta"])

# These should be in .env for production
META_APP_ID = os.getenv("META_APP_ID", "mock_app_id")
META_APP_SECRET = os.getenv("META_APP_SECRET", "mock_app_secret")
REDIRECT_URI = os.getenv("META_REDIRECT_URI", "http://localhost:8000/meta/callback")

# Meta Graph API Base URL
GRAPH_URL = "https://graph.facebook.com/v19.0"

@router.get("/connect")
async def connect_instagram(request: Request, user: User = Depends(get_current_user)):
    if not user or user.role != "creator":
        raise HTTPException(status_code=403, detail="Only creators can connect Instagram accounts.")

    # We are using mock mode to allow sandbox testing without real Facebook App credentials
    if os.getenv("USE_MOCK_DATA") == "true":
        return RedirectResponse(url=f"{REDIRECT_URI}?code=mock_authorization_code", status_code=303)

    # Official OAuth Flow
    scope = "instagram_basic,instagram_manage_insights,pages_show_list,pages_read_engagement"
    auth_url = (
        f"https://www.facebook.com/v19.0/dialog/oauth?"
        f"client_id={META_APP_ID}&redirect_uri={REDIRECT_URI}&scope={scope}&state={user.id}"
    )
    return RedirectResponse(url=auth_url, status_code=303)

@router.get("/callback")
async def meta_callback(
    request: Request,
    code: str,
    state: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user:
        # Fallback if state gets lost, rely on cookie
        pass

    if os.getenv("USE_MOCK_DATA") == "true":
        # Simulate saving a token and fetching initial profile data
        profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == user.id).first()
        if not profile:
            profile = CreatorProfile(user_id=user.id)
            db.add(profile)

        profile.meta_access_token = "mock_long_lived_token_12345"
        profile.instagram_id = "mock_ig_id_999"
        profile.instagram_username = f"mock_{user.username}"
        profile.full_name = f"{user.username.capitalize()} Business"
        profile.biography = "Mock biography fetched from Meta API."
        profile.followers_count = 10500
        profile.business_category = "Software Company"

        db.commit()
        return RedirectResponse(url="/creator/dashboard", status_code=303)

    # --- REAL FLOW ---
    # 1. Exchange code for short-lived access token
    async with httpx.AsyncClient() as client:
        token_res = await client.get(
            f"{GRAPH_URL}/oauth/access_token",
            params={
                "client_id": META_APP_ID,
                "redirect_uri": REDIRECT_URI,
                "client_secret": META_APP_SECRET,
                "code": code
            }
        )
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token from Meta")

        access_token = token_res.json().get("access_token")

        # 2. Get the Instagram Business Account ID attached to the Facebook Page
        # This requires multiple hops in the Graph API: Me -> Pages -> IG Account
        pages_res = await client.get(f"{GRAPH_URL}/me/accounts?access_token={access_token}")
        pages_data = pages_res.json().get("data", [])

        ig_account_id = None
        for page in pages_data:
            page_id = page.get("id")
            ig_res = await client.get(f"{GRAPH_URL}/{page_id}?fields=instagram_business_account&access_token={access_token}")
            ig_data = ig_res.json()
            if "instagram_business_account" in ig_data:
                ig_account_id = ig_data["instagram_business_account"]["id"]
                break

        if not ig_account_id:
            raise HTTPException(status_code=400, detail="No linked Instagram Business Account found.")

        # 3. Fetch Instagram Profile Data
        profile_res = await client.get(
            f"{GRAPH_URL}/{ig_account_id}?fields=username,name,biography,followers_count,ig_id&access_token={access_token}"
        )
        ig_profile_data = profile_res.json()

        # 4. Save to Database
        profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == user.id).first()
        if not profile:
            profile = CreatorProfile(user_id=user.id)
            db.add(profile)

        profile.meta_access_token = access_token
        profile.instagram_id = ig_profile_data.get("ig_id")
        profile.instagram_username = ig_profile_data.get("username")
        profile.full_name = ig_profile_data.get("name")
        profile.biography = ig_profile_data.get("biography")
        profile.followers_count = ig_profile_data.get("followers_count")

        db.commit()

    return RedirectResponse(url="/creator/dashboard", status_code=303)


async def fetch_recent_media_captions(access_token: str, ig_account_id: str) -> list[str]:
    """Helper function to get recent post captions for AI analysis via Meta API."""
    if os.getenv("USE_MOCK_DATA") == "true":
        return ["Launching our new product!", "Check out these features."]

    async with httpx.AsyncClient() as client:
        media_res = await client.get(
            f"{GRAPH_URL}/{ig_account_id}/media?fields=caption&limit=5&access_token={access_token}"
        )
        if media_res.status_code == 200:
            data = media_res.json().get("data", [])
            return [m.get("caption", "") for m in data if "caption" in m]
    return []
