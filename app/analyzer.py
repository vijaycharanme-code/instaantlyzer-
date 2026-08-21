import os
import json
from typing import Dict, Any

import os
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
from google import genai
from google.genai import types

class InstagramAIAnalyzer:
    def __init__(self):
        self.client = None
        if GEMINI_API_KEY:
            self.client = genai.Client(api_key=GEMINI_API_KEY)

        self.model_name = 'gemini-2.5-flash'

    def analyze_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes the raw profile data and uses Gemini to analyze it.
        Returns a structured JSON response.
        """
        if not self.client:
            return {
                "error": "GEMINI_API_KEY is not configured.",
                "business_description": "N/A",
                "category_classification": "N/A",
                "service_tags": [],
                "content_themes": [],
                "target_audience": "N/A",
                "contact_info": "N/A"
            }

        prompt = f"""
        You are an expert AI social media analyst. I will provide you with data extracted from an Instagram business profile.
        Your task is to analyze this data and return a highly structured JSON output containing intelligent insights.

        Here is the profile data:
        - Username: {profile_data.get('username', 'N/A')}
        - Full Name: {profile_data.get('full_name', 'N/A')}
        - Biography: {profile_data.get('biography', 'N/A')}
        - Is Business Account: {profile_data.get('is_business_account', False)}
        - Declared Business Category: {profile_data.get('business_category_name', 'N/A')}
        - External URL: {profile_data.get('external_url', 'N/A')}
        - Recent Captions: {json.dumps(profile_data.get('recent_captions', []))}

        Based on the above information, generate a JSON object with EXACTLY the following keys:
        - "business_description": A clear, concise summary of what this business does (1-2 sentences).
        - "category_classification": The overarching industry or B2B/B2C classification (e.g., "B2B SaaS", "Local B2C Service").
        - "service_tags": An array of specific services or products offered (e.g., ["SEO", "Lead Generation", "Consulting"]).
        - "content_themes": An array of themes extracted from their bio and captions (e.g., ["Educational", "Promotional", "Behind the scenes"]).
        - "target_audience": A short description of who they are trying to reach.
        - "contact_info": Any contact info (email, phone, location) found in the bio. Return "None" if not found.

        Respond ONLY with a valid JSON object. Do not include any markdown formatting like ```json.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            text_response = response.text.strip()
            parsed_data = json.loads(text_response)
            return parsed_data
        except Exception as e:
            raise Exception(f"Failed to analyze data with Gemini API: {str(e)}")

# Example usage for testing
if __name__ == "__main__":
    # Mock data to test the prompt
    mock_data = {
        "username": "test_agency",
        "full_name": "Test Agency",
        "biography": "We build fast websites and scale B2B brands. DM us for a free audit! hello@testagency.com",
        "business_category_name": "Marketing Agency",
        "recent_captions": ["Just finished a new React project!", "5 ways to increase your conversion rate."]
    }
    analyzer = InstagramAIAnalyzer()
    print("Testing analyzer... (Will only work if GEMINI_API_KEY is set)")
    try:
        result = analyzer.analyze_profile(mock_data)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(e)
