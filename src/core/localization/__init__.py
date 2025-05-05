"""Localization package."""

import logging
from typing import Dict, Any

from .en import EN
from .ru import RU

logger = logging.getLogger(__name__)


class LocalizationManager:
    """Simple localization manager for the bot."""

    def __init__(self):
        """Initialize with supported languages."""
        self.messages = {"en": EN, "ru": RU}

    def get_text(self, key: str, lang: str = "en", **kwargs) -> str:
        """Get localized text with optional formatting."""
        try:
            # Get message template (fallback to English if not found)
            text = self.messages.get(lang, {}).get(key)
            if text is None:
                text = self.messages["en"].get(key)
            if text is None:
                return f"Missing translation: {key}"

            # Format with kwargs if provided
            if kwargs:
                try:
                    return text.format(**kwargs)
                except KeyError as e:
                    logger.error(f"Missing format key {e} for message {key}")
                    return text
                except Exception as e:
                    logger.error(f"Error formatting message {key}: {e}")
                return text

            return text

        except Exception as e:
            logger.error(f"Error getting text for key {key}: {e}")
            return f"Error: {str(e)}"

    def get_supported_languages(self) -> list[str]:
        """Get list of supported languages."""
        return list(self.messages.keys())


# Global instance
localization = LocalizationManager()


# Convenience function for getting messages
def get_message(key: str, lang: str = "en", **kwargs) -> str:
    """Get a message with optional formatting."""
    return localization.get_text(key, lang, **kwargs)


__all__ = ["EN", "RU", "get_message", "localization"]
