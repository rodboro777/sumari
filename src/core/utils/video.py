"""Video-related utility functions."""

import re
from typing import Dict, Optional
import aiohttp


def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from various URL formats."""
    if not url:
        return None

    # Regular YouTube URL patterns
    patterns = [
        r"(?:v=|/)([\w-]{11})(?:\?|&|/|$)",  # Standard and mobile URLs
        r"(?:youtu\.be/)([\w-]{11})",  # Short URLs
        r"(?:embed/)([\w-]{11})",  # Embed URLs
    ]

    # Try each pattern
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


async def get_video_info(video_id: str) -> Optional[Dict]:
    """Get video information using YouTube Data API."""
    try:
        # Use YouTube Data API to get video details
        api_key = "AIzaSyA0PWFNr7pw9v5y8JeDSWANXC7H53oid2E"
        url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={api_key}&part=snippet,contentDetails"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                if not data.get("items"):
                    return None

                video = data["items"][0]
                duration = _parse_duration(video["contentDetails"]["duration"])

                return {
                    "title": video["snippet"]["title"],
                    "channel": video["snippet"]["channelTitle"],
                    "duration": duration,
                }
    except Exception:
        return None


def _parse_duration(duration: str) -> str:
    """Parse YouTube duration format (PT1H2M10S) into readable format."""
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not match:
        return "Unknown"

    hours, minutes, seconds = match.groups()
    time_parts = []

    if hours:
        time_parts.append(f"{int(hours)}h")
    if minutes:
        time_parts.append(f"{int(minutes)}m")
    if seconds:
        time_parts.append(f"{int(seconds)}s")

    return " ".join(time_parts) if time_parts else "0s"
