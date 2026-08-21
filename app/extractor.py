import instaloader
import re
import os
from typing import Dict, Any, Optional

class InstagramExtractor:
    def __init__(self):
        self.L = instaloader.Instaloader(
            download_pictures=False,
            download_video_thumbnails=False,
            download_videos=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            request_timeout=15, # Added timeout to prevent hanging forever
        )

    def extract_username_from_url(self, url: str) -> Optional[str]:
        """
        Extracts the username from a typical Instagram URL.
        """
        pattern = r"(?:https?:\/\/)?(?:www\.)?instagram\.com\/([a-zA-Z0-9._]+)\/?"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    def fetch_profile_data(self, username: str) -> Dict[str, Any]:
        """
        Fetches public profile data and a few recent posts to feed into the AI.
        """
        # FOR TESTING/MVP Purposes: if we are in a sandbox that blocks Instagram scraping,
        # we can provide a mock response if a specific environment variable is set.
        if os.getenv("USE_MOCK_DATA") == "true":
            return {
                "username": username,
                "full_name": f"{username.capitalize()} Business",
                "biography": "We are a top-tier digital marketing agency. Helping B2B SaaS companies scale. Contact us at hello@example.com",
                "followers": 15000,
                "following": 500,
                "is_business_account": True,
                "business_category_name": "Marketing Agency",
                "external_url": "https://example.com",
                "recent_captions": [
                    "🚀 Launching our new SEO course next week! Stay tuned.",
                    "We helped our client achieve a 300% increase in leads using our proprietary ad targeting methods.",
                    "Tip of the day: Always structure your data for better AI insights! 🧠 #Data #AI #Marketing"
                ]
            }

        try:
            profile = instaloader.Profile.from_username(self.L.context, username)

            data = {
                "username": profile.username,
                "full_name": profile.full_name,
                "biography": profile.biography,
                "followers": profile.followers,
                "following": profile.followees,
                "is_business_account": profile.is_business_account,
                "business_category_name": profile.business_category_name,
                "external_url": profile.external_url,
                "recent_captions": []
            }

            count = 0
            for post in profile.get_posts():
                if count >= 3: # Reduced to 3 to be faster and less likely to hit rate limits
                    break
                if post.caption:
                    data["recent_captions"].append(post.caption)
                count += 1

            return data
        except instaloader.exceptions.ProfileNotExistsException:
            raise Exception(f"Profile '{username}' does not exist.")
        except Exception as e:
            raise Exception(f"Error fetching data for '{username}'. The profile might be private or rate limited: {str(e)}")
