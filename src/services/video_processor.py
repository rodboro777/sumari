"""Video and text processing service for generating summaries."""

import logging
from typing import Dict, Optional, Tuple
import torch
from transformers import DistilBertTokenizer, DistilBertModel
import numpy as np
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from src.core.utils.rate_limit import check_rate_limit, check_monthly_limit
from src.database import db_manager
from src.services import monitoring_service   
import google.generativeai as genai
from src.config import MAX_SUMMARY_LENGTH
from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup
import requests
from src.config import GEMINI_API_KEY


class VideoProcessor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VideoProcessor, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
    ):
        """Initialize video processor with required dependencies."""
        if not hasattr(self, 'initialized'):
            self.db = db_manager
            self.monitoring = monitoring_service
            self.logger = logging.getLogger("video_processor")
            self.metrics = metrics_collector

            # Initialize Gemini
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            
            # Initialize DistilBERT
            self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-multilingual-cased')
            self.bert_model = DistilBertModel.from_pretrained('distilbert-base-multilingual-cased')
            self.bert_model.eval()  # Set to evaluation mode
            self.initialized = True

    async def process_link(self, link: str, user_id: int, language: str = "en", summary_type: str = "both") -> Tuple[bool, Dict]:
        """Process a link and generate summary.
        
        Args:
            link: URL to process
            user_id: User ID
            language: Language code
            summary_type: Type of summary to generate. One of:
                - "gemini": Use only Gemini
                - "bert": Use DistilBERT + Gemini
                - "both": Generate both summaries (default)
        """
        try:
            # Check rate limits
            if summary_type != "test":
                rate_limit_ok = await check_rate_limit(user_id)
                if not rate_limit_ok:
                    return False, {"error": "Rate limit exceeded"}

                monthly_limit_ok = await check_monthly_limit(user_id)
                if not monthly_limit_ok:
                    return False, {"error": "Monthly limit exceeded"}

            # Extract content from URL
            content = await self._extract_content(link)
            if not content:
                return False, {"error": "Could not extract content from URL"}

            results = {}
            
            # Generate summaries based on requested type
            if summary_type in ["gemini", "both"]:
                success, gemini_result = await self._generate_gemini_summary(content, language, user_id)
                if success:
                    results["gemini_summary"] = gemini_result["summary"]
                else:
                    return False, gemini_result

            if summary_type in ["bert", "both"]:
                success, bert_result = await self._generate_bert_summary(content, language, user_id)
                if success:
                    results["bert_summary"] = bert_result["summary"]
                else:
                    return False, bert_result

            # Add metadata
            results.update({
                "url": link,
                "content_length": len(content),
                "language": language
            })

            return True, results

        except Exception as e:
            self.logger.error(f"Error processing link: {str(e)}", exc_info=True)
            return False, {"error": str(e)}

    async def _extract_content(self, url: str) -> Optional[str]:
        """Extract content from URL."""
        try:
            if "youtube.com" in url or "youtu.be" in url:
                # Extract YouTube transcript
     
                video_id = url.split("v=")[-1].split("&")[0]
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "ru"])
                return " ".join([t["text"] for t in transcript])
            else:
                # Extract article content
            
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup.get_text()
        except Exception as e:
            self.logger.error(f"Error extracting content: {str(e)}")
            return None

    async def _generate_gemini_summary(self, content: str, language: str, user_id: int) -> Tuple[bool, Dict]:
        """Generate summary using only Gemini."""
        try:
            # Get user's summary length preference
            user_prefs = self.db.get_user_preferences(user_id)
            summary_length = user_prefs.get("summary_length", "medium")
            
            # Adjust prompt based on summary length
            detail_level = {
                "short": "Create a brief overview focusing only on the most important points",
                "medium": "Create a balanced summary covering main points and key details",
                "detailed": "Create a comprehensive summary including main points, key details, and supporting information"
            }.get(summary_length, "Create a balanced summary covering main points and key details")
            
            # Prepare prompt
            prompt = (
                f"Generate a summary of this content in {language}. {detail_level}:\n\n{content}"
            )
            
            # Generate summary
            response = await self.model.generate_content(prompt)
            summary = response.text

            # Track metrics
            self.metrics.log_summary_generation(
                user_id=user_id,
                char_count=len(summary),
                success=True,
                summary_type="gemini"
            )

            return True, {"summary": summary}

        except Exception as e:
            self.logger.error(f"Error generating Gemini summary: {str(e)}")
            return False, {"error": str(e)}

    async def _generate_bert_summary(self, content: str, language: str, user_id: int) -> Tuple[bool, Dict]:
        """Generate summary using DistilBERT preprocessing + Gemini."""
        try:
            # Get user's summary length preference
            user_prefs = self.db.get_user_preferences(user_id)
            summary_length = user_prefs.get("summary_length", "medium")
            
            # Adjust number of sentences based on summary length
            max_sentences = {
                "short": 3,
                "medium": 5,
                "detailed": 8
            }.get(summary_length, 5)
            
            # Preprocess with DistilBERT
            inputs = self.tokenizer(content, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
            
            # Get embeddings and find key sentences
            embeddings = outputs.last_hidden_state.mean(dim=1).numpy()
            sentences = content.split(". ")
            sentence_embeddings = []
            
            # Generate embeddings for each sentence
            for sentence in sentences:
                if sentence:
                    inputs = self.tokenizer(sentence, return_tensors="pt", truncation=True)
                    with torch.no_grad():
                        outputs = self.bert_model(**inputs)
                    sentence_embeddings.append(outputs.last_hidden_state.mean(dim=1).numpy())
            
            # Find most relevant sentences using cosine similarity
            similarities = []
            for sent_emb in sentence_embeddings:
                similarity = np.dot(embeddings, sent_emb.T) / (np.linalg.norm(embeddings) * np.linalg.norm(sent_emb))
                similarities.append(float(similarity))
            
            # Get top sentences based on user's preference
            top_indices = np.argsort(similarities)[-max_sentences:]
            top_sentences = [sentences[i] for i in sorted(top_indices)]
            
            # Use Gemini to polish the summary
            key_points = ". ".join(top_sentences)
            
            # Adjust prompt based on summary length
            detail_level = {
                "short": "Create a brief overview focusing only on the most important points",
                "medium": "Create a balanced summary covering main points and key details",
                "detailed": "Create a comprehensive summary including main points, key details, and supporting information"
            }.get(summary_length, "Create a balanced summary covering main points and key details")
            
            prompt = (
                f"Based on these key points, {detail_level} in {language}:\n\n{key_points}"
            )
            
            response = await self.model.generate_content(prompt)
            summary = response.text

            # Track metrics
            self.metrics.log_summary_generation(
                user_id=user_id,
                char_count=len(summary),
                success=True,
                summary_type="bert"
            )

            return True, {"summary": summary}

        except Exception as e:
            self.logger.error(f"Error generating BERT summary: {str(e)}")
            return False, {"error": str(e)}

    async def send_summary(self, bot, chat_id: int, summary_data: Dict, language: str) -> None:
        """Send summary to user."""
        try:
            # Format message
            message = f"*Summary Results*\n\n"
            
            if "gemini_summary" in summary_data:
                message += "*Gemini Summary:*\n"
                message += f"{summary_data['gemini_summary']}\n\n"
                
            if "bert_summary" in summary_data:
                message += "*DistilBERT + Gemini Summary:*\n"
                message += f"{summary_data['bert_summary']}\n\n"
            
            message += f"📊 Content length: {summary_data['content_length']} characters"

            # Send message
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN_V2
            )

        except Exception as e:
            self.logger.error(f"Error sending summary: {str(e)}")
            await bot.send_message(
                chat_id=chat_id,
                text=f"Error sending summary: {str(e)}",
                parse_mode=ParseMode.MARKDOWN_V2
            )

# Export the class directly, no need to create instance
