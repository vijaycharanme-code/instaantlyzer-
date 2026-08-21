from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

from app.extractor import InstagramExtractor
from app.analyzer import InstagramAIAnalyzer

app = FastAPI(title="Instagram AI Analyzer API")

# Setup templates and static files if needed
templates = Jinja2Templates(directory="app/templates")
# Create static dir just in case we need it, though not strictly necessary for MVP
os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

extractor = InstagramExtractor()
analyzer = InstagramAIAnalyzer()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_url(request: Request, url: str = Form(...)):
    try:
        # 1. Extract username from URL
        username = extractor.extract_username_from_url(url)
        if not username:
            return templates.TemplateResponse(request, "index.html", {
                "request": request,
                "error": "Invalid Instagram URL provided.",
                "url": url
            })

        # 2. Extract Data
        try:
            profile_data = extractor.fetch_profile_data(username)
        except Exception as e:
            return templates.TemplateResponse(request, "index.html", {
                "request": request,
                "error": f"Extraction failed: {str(e)}",
                "url": url
            })

        # 3. Analyze Data
        try:
            analysis = analyzer.analyze_profile(profile_data)
        except Exception as e:
            return templates.TemplateResponse(request, "index.html", {
                "request": request,
                "error": f"AI Analysis failed: {str(e)}",
                "url": url
            })

        # Merge for view
        result = {
            "profile": profile_data,
            "analysis": analysis
        }

        return templates.TemplateResponse(request, "index.html", {
            "request": request,
            "result": result,
            "url": url
        })

    except Exception as e:
        return templates.TemplateResponse(request, "index.html", {
            "request": request,
            "error": f"An unexpected error occurred: {str(e)}",
            "url": url
        })

# Optional: pure API endpoint for integrations
@app.post("/api/analyze")
async def api_analyze(url: str):
    username = extractor.extract_username_from_url(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Instagram URL")

    try:
        profile_data = extractor.fetch_profile_data(username)
        analysis = analyzer.analyze_profile(profile_data)
        return {
            "status": "success",
            "data": {
                "profile": profile_data,
                "analysis": analysis
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
