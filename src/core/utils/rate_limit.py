"""Rate limiting utilities."""

import time
from src.config import RATE_LIMIT_SECONDS

# Rate limiting
RATE_LIMIT = {}  # {user_id: last_request_time}


def check_rate_limit(user_id: int) -> bool:
    """Check if user has exceeded rate limit."""
    current_time = time.time()
    if user_id in RATE_LIMIT:
        last_request = RATE_LIMIT[user_id]
        if current_time - last_request < RATE_LIMIT_SECONDS:
            return False

    RATE_LIMIT[user_id] = current_time
    return True
