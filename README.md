# InstaIntel: AI-Based Instagram Business Profile Analyzer

InstaIntel is a fast, web-based tool and API that accepts an Instagram business profile URL, extracts publicly available data (bio, followers, recent captions), and leverages the **Google Gemini API** to analyze and generate structured insights about the business.

This tool solves the problem of unstructured social media data by transforming it into actionable JSON (Business description, Category classification, Service tags, Content themes, Target audience, etc.), ready for integration into CRM or lead generation systems.

## Features
- **UI Dashboard**: Clean interface built with TailwindCSS to input URLs and view insights.
- **FastAPI Backend**: Modern, high-performance async backend.
- **Data Extraction**: Uses `instaloader` to pull public metadata and recent captions without needing a full browser instance.
- **AI Analysis**: Uses the official `google-genai` SDK and `gemini-2.5-flash` model to intelligently parse and categorize unstructured text into clean JSON.
- **API Endpoint**: Includes a `/api/analyze` endpoint to integrate directly into other tools.

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

   *(Optional) If you are testing locally and want to avoid Instagram rate limits or IP blocks, you can enable mock data by uncommenting `USE_MOCK_DATA=true` in the `.env` file.*

4. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the tool:**
   Open your browser and navigate to `http://localhost:8000`.

## API Usage

You can also use the tool purely as a backend API.

**Endpoint:** `POST /api/analyze`
**Content-Type:** `application/x-www-form-urlencoded` or query parameter.

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/analyze?url=https://www.instagram.com/nike"
```

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "profile": {
      "username": "nike",
      "full_name": "Nike",
      "biography": "Spotlighting athletes...",
      "followers": 300000000,
      "...": "..."
    },
    "analysis": {
      "business_description": "A global sports apparel and footwear company.",
      "category_classification": "B2C Retail",
      "service_tags": ["Shoes", "Apparel", "Athletic Gear"],
      "content_themes": ["Motivation", "Sports", "Product Drops"],
      "target_audience": "Athletes and fitness enthusiasts globally.",
      "contact_info": "None"
    }
  }
}
```

## Note on Instagram Extraction
Extracting data from Instagram can be volatile due to aggressive anti-bot measures. The current extractor uses `instaloader` to fetch data anonymously. If you run into `ProfileNotExistsException` or connection resets, you may be temporarily rate-limited by Instagram. Using authenticated sessions or proxies may be required for high-volume production use.
