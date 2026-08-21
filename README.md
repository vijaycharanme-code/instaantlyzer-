# InstaIntel: AI-Based Instagram Business Profile Analyzer Directory

InstaIntel is a fast, web-based platform that allows Instagram Creators to connect their business profiles via the official Meta Graph API. The system then leverages the **Google Gemini API** to analyze and generate structured insights about the business. Regular users can register and browse or search this directory of intelligent AI-analyzed profiles.

## Features
- **UI Dashboard**: Clean interface built with TailwindCSS for both Creators and Users.
- **FastAPI Backend**: Modern, high-performance async backend.
- **SQLite & SQLAlchemy**: User registration, login, and secure sessions.
- **Meta Graph API**: Official OAuth flow to connect Instagram Business accounts securely.
- **AI Analysis**: Uses the official `google-genai` SDK and `gemini-2.5-flash` model to intelligently parse and categorize unstructured text into clean JSON.

## Setup Instructions

1. **Clone the repository and navigate to the directory:**
   ```bash
   cd instagram-analyzer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and add your **Google Gemini API Key**. You can get one from [Google AI Studio](https://aistudio.google.com/).
   ```env
   GEMINI_API_KEY=your_actual_key_here
   ```

   *(Optional) If you are testing locally and want to avoid setting up a real Meta Developer App, you can enable mock data by uncommenting `USE_MOCK_DATA=true` in the `.env` file.*

4. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the tool:**
   Open your browser and navigate to `http://localhost:8000`. You can register as a "Creator" to mock connecting an Instagram account, and register as a "User" to view the searchable directory.
