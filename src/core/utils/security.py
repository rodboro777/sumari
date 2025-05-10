"""Security utilities for input validation and rate limiting."""

import re
import time
import ipaddress
from typing import Optional, Tuple, List
from collections import defaultdict
from datetime import datetime, timedelta
import logging
from telegram import Update
from src.config import (
    MAX_MESSAGE_LENGTH,
    RATE_LIMIT_SECONDS,
    MAX_REQUESTS_PER_MINUTE,
    BLOCKED_PATTERNS,
)

logger = logging.getLogger(__name__)

# Rate limiting storage
user_requests = defaultdict(list)
user_last_request = defaultdict(float)

# Additional security patterns
DANGEROUS_PATTERNS = [
    r"(?i)(select|insert|update|delete|drop|union|exec|declare).*",  # SQL injection
    r"<script.*?>.*?</script>",  # XSS
    r"(?i)(eval|setTimeout|setInterval)\s*\(",  # JavaScript injection
    r"(?i)document\.(location|cookie|write)",  # DOM manipulation
    r"(?i)system\s*\(",  # Command injection
]

# Blocked URL patterns (excluding YouTube)
BLOCKED_URL_PATTERNS = [
    r"(?i)(?:ftp|file):\/\/.*",  # Block FTP and FILE protocols
    r"(?i)(?:https?:\/\/(?!(?:www\.)?(?:youtube\.com|youtu\.be))).*",  # Block non-YouTube HTTP(S) URLs
]

# YouTube URL pattern
YOUTUBE_URL_PATTERN = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?([a-zA-Z0-9_-]{11})"


def is_youtube_url(text: str) -> bool:
    """Check if the text is a valid YouTube URL.

    Args:
        text: Text to check

    Returns:
        bool: Whether the text is a valid YouTube URL
    """
    return bool(re.match(YOUTUBE_URL_PATTERN, text))


def is_valid_ip(ip: str, allowed_ranges: List[str] = None) -> bool:
    """Validate if an IP is within allowed ranges.

    Args:
        ip: IP address to check
        allowed_ranges: List of allowed IP ranges in CIDR notation

    Returns:
        bool: Whether the IP is valid and allowed
    """
    try:
        ip_addr = ipaddress.ip_address(ip)
        if not allowed_ranges:
            return True

        return any(
            ip_addr in ipaddress.ip_network(allowed_range)
            for allowed_range in allowed_ranges
        )
    except ValueError:
        return False


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks.

    Args:
        text: Raw input text

    Returns:
        Sanitized text string
    """
    if not text:
        return ""

    # Remove any potential HTML/script tags
    text = re.sub(r"<[^>]*>", "", text)

    # Remove any potential SQL injection patterns
    text = re.sub(r'[\'";\-]', "", text)

    # Remove any control characters
    text = "".join(char for char in text if ord(char) >= 32)

    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text):
            logger.warning(f"Dangerous pattern detected in input: {pattern}")
            text = re.sub(pattern, "", text)

    return text.strip()


def check_message_length(text: str) -> Tuple[bool, Optional[str]]:
    """Check if message length is within allowed limits.

    Args:
        text: Message text to check

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text:
        return False, "Empty message"

    if len(text) > MAX_MESSAGE_LENGTH:
        return False, f"Message too long (max {MAX_MESSAGE_LENGTH} characters)"

    return True, None


def check_blocked_patterns(text: str) -> Tuple[bool, Optional[str]]:
    """Check for blocked patterns in text.

    Args:
        text: Text to check

    Returns:
        Tuple of (is_allowed, error_message)
    """
    # Check custom blocked patterns
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, "Message contains blocked content"

    # Check dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, "Message contains potentially dangerous content"

    return True, None


def check_rate_limit(user_id: int) -> Tuple[bool, Optional[str]]:
    """Check if user has exceeded rate limits.

    Args:
        user_id: Telegram user ID

    Returns:
        Tuple of (is_allowed, error_message)
    """
    current_time = time.time()

    # Clean old requests
    user_requests[user_id] = [
        req_time for req_time in user_requests[user_id] if req_time > current_time - 60
    ]

    # Check requests per minute
    if len(user_requests[user_id]) >= MAX_REQUESTS_PER_MINUTE:
        return (
            False,
            f"Rate limit exceeded. Maximum {MAX_REQUESTS_PER_MINUTE} requests per minute.",
        )

    # Check time between requests
    last_request = user_last_request[user_id]
    if current_time - last_request < RATE_LIMIT_SECONDS:
        return (
            False,
            f"Please wait {int(RATE_LIMIT_SECONDS - (current_time - last_request))} seconds",
        )

    # Update rate limit tracking
    user_requests[user_id].append(current_time)
    user_last_request[user_id] = current_time

    return True, None


def check_blocked_urls(text: str) -> Tuple[bool, Optional[str]]:
    """Check if text contains blocked URLs.

    Args:
        text: Text to check

    Returns:
        Tuple of (is_allowed, error_message)
    """
    # Allow YouTube URLs
    if is_youtube_url(text):
        return True, None

    # Check for blocked URL patterns
    for pattern in BLOCKED_URL_PATTERNS:
        if re.search(pattern, text):
            return False, "blocked_url"

    return True, None


async def security_check(update: Update) -> Tuple[bool, Optional[str]]:
    """Perform all security checks on an update.

    Args:
        update: Telegram update to check

    Returns:
        Tuple of (is_allowed, error_message)
    """
    try:
        user_id = update.effective_user.id

        # Check rate limits
        is_allowed, error = check_rate_limit(user_id)
        if not is_allowed:
            return False, error

        # For text messages, perform content checks
        if update.message and update.message.text:
            text = update.message.text

            # Check message length
            is_valid, error = check_message_length(text)
            if not is_valid:
                return False, error

            # Check for blocked patterns
            is_allowed, error = check_blocked_patterns(text)
            if not is_allowed:
                return False, error

            # Check for blocked URLs
            is_allowed, error = check_blocked_urls(text)
            if not is_allowed:
                return False, error

            # Check if it's a YouTube URL
            if not is_youtube_url(text):
                logger.info(
                    f"Received non-URL text from user {user_id}: {text[:50]}..."
                )
                return False, "not_youtube_url"

            # Sanitize input (for storage/logging only)
            sanitized_text = sanitize_input(text)
            if sanitized_text != text:
                logger.warning(
                    f"Text sanitized for user {user_id}: {text[:50]} -> {sanitized_text[:50]}"
                )

        return True, None

    except Exception as e:
        logger.error(f"Error in security check: {str(e)}")
        return False, "security_check_failed"
