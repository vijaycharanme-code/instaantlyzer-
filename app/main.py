import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

# Import routers and models BEFORE creating tables so SQLAlchemy knows about them
from app.models import Base
from app.auth import router as auth_router
from app.meta_api import router as meta_router
from app.creator_router import router as creator_router
from app.user_router import router as user_router

# Import database and create tables
from app.database import engine
Base.metadata.create_all(bind=engine)

app = FastAPI(title="InstaIntel Platform")

# Add SessionMiddleware for cookie-based sessions
SESSION_SECRET = os.getenv("SESSION_SECRET", "super-secret-key-change-in-production")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# We can keep static files if needed
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include Routers
app.include_router(auth_router)
app.include_router(meta_router)
app.include_router(creator_router)
app.include_router(user_router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Check if logged in to redirect appropriately
    user_id = request.session.get("user_id")
    role = request.session.get("role")

    if user_id:
        if role == "creator":
            return RedirectResponse(url="/creator/dashboard")
        elif role == "user":
            return RedirectResponse(url="/user/dashboard")

    # Otherwise go to login
    return RedirectResponse(url="/auth/login")
