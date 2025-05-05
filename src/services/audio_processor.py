"""Audio processing service for generating audio summaries using Google Cloud Text-to-Speech."""

import logging
import asyncio
from typing import Dict, Optional, Tuple
import os
from datetime import datetime
from google.cloud import storage
from google.cloud import texttospeech
from src.database.db_manager import DatabaseManager
from src.services.monitoring import MonitoringService
from src.config import GCP_BUCKET_NAME
from pathlib import Path
import aiohttp
import time

class AudioProcessor:
    def __init__(
        self,
        db_manager: DatabaseManager,
        monitoring: MonitoringService,
    ):
        """Initialize audio processor with required dependencies."""
        self.db = db_manager
        self.monitoring = monitoring
        self.logger = logging.getLogger("audio_processor")
        self.gcp_bucket_name = GCP_BUCKET_NAME
        
        # Get path to credentials file relative to src directory
        src_dir = Path(__file__).parent.parent  # This gets us to the src directory
        credentials_path = src_dir.parent / 'sumari-458514-f6d0db13e3ec.json'  # Go up one level to project root
        
        try:
            self.logger.info(f"Using GCP credentials from: {credentials_path}")
            # Initialize Storage client
            self.storage_client = storage.Client.from_service_account_json(str(credentials_path))
            self.bucket = self.storage_client.bucket(self.gcp_bucket_name)
            
            # Initialize Text-to-Speech client
            self.tts_client = texttospeech.TextToSpeechClient.from_service_account_json(str(credentials_path))
            
            # Test bucket access
            list(self.bucket.list_blobs(max_results=1))
            self.logger.info("Successfully connected to GCP Storage and Text-to-Speech")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize GCP services: {str(e)}")
            raise

    async def generate_audio_summary(
        self, text: str, voice: str = "en-US-Standard-D", user_id: int = 0
    ) -> Tuple[bool, Dict]:
        """Generate audio summary using Google Cloud Text-to-Speech."""
        start_time = time.time()
        try:
            # Generate a unique filename based on text content and voice
            filename = f"{hash(text + voice)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            blob_name = f"summaries/{filename}"
            
            # Check if audio already exists in cache
            blob = self.bucket.blob(blob_name)
            if blob.exists():
                # Log cached audio usage
                processing_time = time.time() - start_time
                self.db.log_api_usage(
                    user_id=user_id,
                    api_name="audio_processing",
                    status="success",
                    details={
                        "processing_time": processing_time,
                        "is_audio": True,
                        "cached": True
                    }
                )
                return True, {
                    "audio_url": f"https://storage.googleapis.com/{self.gcp_bucket_name}/{blob_name}",
                    "blob_name": blob_name,
                    "cached": True,
                    "format": "mp3",
                    "voice": voice
                }
            
            # Set the text input to be synthesized
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Build the voice request
            voice_params = texttospeech.VoiceSelectionParams(
                language_code=voice[:5],  # e.g., "en-US"
                name=voice,  # e.g., "en-US-Standard-D"
            )

            # Select the type of audio file
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,
                pitch=0.0,
            )

            # Perform the text-to-speech request
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config
            )
            
            # Upload to GCP Storage
            blob.upload_from_string(
                response.audio_content,
                content_type="audio/mp3"
            )
            
            # Generate the public URL without using ACLs
            public_url = f"https://storage.googleapis.com/{self.gcp_bucket_name}/{blob_name}"
            
            # Log successful audio generation
            processing_time = time.time() - start_time
            self.db.log_api_usage(
                user_id=user_id,
                api_name="audio_processing",
                status="success",
                details={
                    "processing_time": processing_time,
                    "is_audio": True,
                    "cached": False
                }
            )
            
            return True, {
                "audio_url": public_url,
                "blob_name": blob_name,
                "cached": False,
                "format": "mp3",
                "voice": voice
            }

        except Exception as e:
            # Log error
            processing_time = time.time() - start_time
            self.db.log_api_usage(
                user_id=user_id,
                api_name="audio_processing",
                status="failed",
                details={
                    "processing_time": processing_time,
                    "error": str(e)
                }
            )
            self.logger.error(f"Error generating audio summary: {str(e)}")
            return False, {"error": str(e)}

    async def generate_demo_audio(
        self, text: str, language: str = "en"
    ) -> Tuple[bool, Dict]:
        """Generate a demo audio summary with limited duration."""
        # Map language codes to appropriate voices
        voice_map = {
            "en": "en-US-Standard-D",  # Male voice
            "es": "es-ES-Standard-C",  # Male voice
            "pt": "pt-BR-Standard-B",  # Male voice
            "hi": "hi-IN-Standard-B",  # Male voice
            "ru": "ru-RU-Standard-D",  # Male voice
            "ar": "ar-XA-Standard-B",  # Male voice
            "id": "id-ID-Standard-B",  # Male voice
            "fr": "fr-FR-Standard-D",  # Male voice
            "de": "de-DE-Standard-D",  # Male voice
            "tr": "tr-TR-Standard-B",  # Male voice
            "uk": "uk-UA-Standard-A",  # Male voice
        }
        
        # Get appropriate voice for language or default to English
        voice = voice_map.get(language, "en-US-Standard-D")
        
        # Truncate text for demo (first 100 words or so)
        demo_text = " ".join(text.split()[:100]) + "..."

        try:
            result, data = await self.generate_audio_summary(demo_text, voice=voice)
            
            if not result:
                return False, data

            # Add demo flag to response
            data["is_demo"] = True
            data["full_text_available"] = len(text.split()) > 100

            return True, data

        except Exception as e:
            self.logger.error(f"Error generating demo audio: {str(e)}")
            return False, {"error": str(e)}

    def cleanup_old_audio_files(self, max_age_hours: int = 24):
        """Clean up old audio files from GCP Storage."""
        try:
            current_time = datetime.now()
            blobs = self.bucket.list_blobs(prefix="summaries/")
            
            for blob in blobs:
                age = (current_time - blob.time_created).total_seconds() / 3600
                if age > max_age_hours:
                    blob.delete()
                    
        except Exception as e:
            self.logger.error(f"Error cleaning up old audio files: {str(e)}")

    async def get_available_voices(self, language: str = None) -> Tuple[bool, Dict]:
        """Get list of available voices, optionally filtered by language."""
        try:
            # List all available voices
            response = self.tts_client.list_voices()
            voices = []
            
            for voice in response.voices:
                if not language or voice.language_codes[0].startswith(language):
                    voices.append({
                        "name": voice.name,
                        "language_codes": voice.language_codes,
                        "ssml_gender": texttospeech.SsmlVoiceGender(voice.ssml_gender).name,
                        "natural_sample_rate_hertz": voice.natural_sample_rate_hertz,
                    })
            
            return True, {
                "voices": voices,
                "total": len(voices),
                "languages": list(set(lang[:2] for v in voices for lang in v["language_codes"]))
            }

        except Exception as e:
            self.logger.error(f"Error getting available voices: {str(e)}")
            return False, {"error": str(e)}

    async def get_voice_details(self, voice_id: str) -> Tuple[bool, Dict]:
        """Get detailed information about a specific voice."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/tts/voices/{voice_id}",
                    headers=self.headers,
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        return False, {"error": error_data.get("message", "API error")}

                    data = await response.json()
                    return True, {
                        "voice_id": data["voice_id"],
                        "name": data["name"],
                        "language": data["language"],
                        "gender": data["gender"],
                        "age": data["age"],
                        "accent": data["accent"],
                        "sample_url": data["sample_url"],
                        "supported_formats": data["supported_formats"],
                    }

        except Exception as e:
            self.logger.error(f"Error getting voice details: {str(e)}")
            return False, {"error": str(e)}

    async def get_audio_status(self, audio_id: str) -> Tuple[bool, Dict]:
        """Get the status of an audio generation request."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/tts/status/{audio_id}",
                    headers=self.headers,
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        return False, {"error": error_data.get("message", "API error")}

                    data = await response.json()
                    return True, {
                        "status": data["status"],
                        "progress": data["progress"],
                        "estimated_time_remaining": data["estimated_time_remaining"],
                        "audio_url": data.get("audio_url"),
                        "error": data.get("error"),
                    }

        except Exception as e:
            self.logger.error(f"Error getting audio status: {str(e)}")
            return False, {"error": str(e)}

    async def test_tts_permissions(self) -> Tuple[bool, str]:
        """Test if we have proper permissions for Text-to-Speech API."""
        try:
            # Try to list voices - this will fail if we don't have proper permissions
            response = self.tts_client.list_voices()
            voice_count = len(response.voices)
            
            # Try to generate a very short audio - this will fail if API is not enabled
            synthesis_input = texttospeech.SynthesisInput(text="Test.")
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Standard-D"
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            return True, f"✅ TTS API is properly configured. Found {voice_count} available voices."
            
        except Exception as e:
            error_message = str(e)
            if "Permission denied" in error_message:
                return False, "❌ Permission denied. Make sure the service account has the 'Cloud Text-to-Speech API User' role."
            elif "API has not been used in project" in error_message:
                return False, "❌ Text-to-Speech API is not enabled. Please enable it in the Google Cloud Console."
            else:
                return False, f"❌ Error testing TTS permissions: {error_message}" 