from typing import Dict, List, Optional, Tuple
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
import google.generativeai as genai
import time
from datetime import datetime
import logging

from src.database.db_manager import DatabaseManager
from src.services.monitoring import MonitoringService


class VideoProcessor:
    def __init__(
        self,
        db_manager: DatabaseManager,
        monitoring: MonitoringService,
        gemini_api_key: str,
    ):
        self.db = db_manager
        self.monitoring = monitoring
        self.logger = logging.getLogger("video_processor")

        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    async def process_video(
        self, video_id: str, user_id: int, user_preferences: Dict
    ) -> Tuple[bool, str]:
        """
        Process a video and generate its summary.
        Returns a tuple of (success, result/error_message)
        """
        start_time = time.time()
        try:
            # Get transcript
            transcript = await self._get_transcript(video_id)
            if not transcript:
                return False, "No transcript available for this video"

            # Generate summary
            summary = await self._generate_summary(
                transcript,
                user_preferences.get("language", "en"),
                user_preferences.get("summary_length", "medium"),
            )

            # Log success and update usage statistics
            processing_time = time.time() - start_time
            self.monitoring.track_api_usage("video_processing", True, processing_time)

            # Update database with usage statistics
            self.db.log_api_usage(
                user_id=user_id,
                api_name="video_processing",
                status="success",
                details={"processing_time": processing_time, "is_audio": False},
            )

            return True, summary

        except Exception as e:
            # Log error
            processing_time = time.time() - start_time
            self.monitoring.track_api_usage("video_processing", False, processing_time)
            self.monitoring.track_error("video_processing", str(e), user_id)

            # Update database with error
            self.db.log_api_usage(
                user_id=user_id,
                api_name="video_processing",
                status="failed",
                details={"processing_time": processing_time, "error": str(e)},
            )

            return False, str(e)

    async def _get_transcript(self, video_id: str) -> Optional[str]:
        """Get video transcript."""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, languages=["en", "ru"]
            )
            return " ".join([t["text"] for t in transcript])
        except NoTranscriptFound:
            self.logger.warning(f"No transcript found for video {video_id}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting transcript: {str(e)}")
            raise

    async def _generate_summary(
        self, text: str, language: str = "en", length: str = "medium"
    ) -> str:
        """Generate summary using Gemini."""
        # Define length-based prompts
        length_prompts = {
            "short": {
                "en": "Create a brief summary focusing only on the main points",
                "ru": "Создайте краткое резюме, фокусируясь только на основных моментах",
            },
            "medium": {
                "en": "Create a balanced summary with moderate detail",
                "ru": "Создайте сбалансированное резюме с умеренным количеством деталей",
            },
            "detailed": {
                "en": "Create a comprehensive detailed summary",
                "ru": "Создайте подробное и всестороннее резюме",
            },
        }

        # Select prompt based on language and length
        prompt_style = length_prompts.get(length, length_prompts["medium"]).get(
            language, length_prompts[length]["en"]
        )

        try:
            # Generate summary
            if language == "en":
                prompt = (
                    f"Summarize this text in a detailed but clear way in English. {prompt_style}:\n\n"
                    f"{text}\n\n"
                )
            elif language == "ru":
                prompt = (
                    f"Пожалуйста, предоставьте подробное, но понятное резюме следующего текста "
                    f"на русском языке. {prompt_style}:\n\n{text}\n\n"
                )

            response = self.model.generate_content(prompt)
            return self._format_summary(response.text)
        except Exception as e:
            if any(keyword in str(e).lower() for keyword in ["quota", "rate", "limit"]):
                raise Exception("API rate limit exceeded. Please try again later.")
            raise

    def _format_summary(self, text: str) -> str:
        """Format the summary for better readability in Telegram."""
        # Remove extra newlines
        text = "\n".join(line.strip() for line in text.split("\n") if line.strip())

        # Add bullet points to lists
        lines = text.split("\n")
        formatted_lines = []
        for line in lines:
            if line.startswith(("•", "-", "*")):
                formatted_lines.append(f"• {line.lstrip('•-* ')}")
            else:
                formatted_lines.append(line)

        return "\n".join(formatted_lines)
