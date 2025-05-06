"""Rate limiting and usage tracking utilities."""

from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
from src.config import RATE_LIMIT_SECONDS, TIER_LIMITS
from src.database.db_manager import db_manager

# Request rate limiting
RATE_LIMIT: Dict[int, float] = {}


def check_rate_limit(user_id: int) -> bool:
    """Check if user is rate limited for requests."""
    current_time = datetime.now(timezone.utc).timestamp()
    last_request = RATE_LIMIT.get(user_id, 0)

    if current_time - last_request < RATE_LIMIT_SECONDS:
        return False

    RATE_LIMIT[user_id] = current_time
    return True


def check_monthly_limit(user_id: int) -> Tuple[bool, Optional[str], Optional[int]]:
    """Check if user has exceeded their monthly summary limit.
    
    Returns:
        Tuple[bool, Optional[str], Optional[int]]: (can_use, error_message, summaries_used)
    """
    try:
        # Get user data
        user_data = db_manager.get_user_data(user_id)
        tier = user_data.get("premium", {}).get("tier", "free")
        
        # Get tier limits
        tier_config = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
        monthly_limit = tier_config["monthly_summaries"]
        
        # Check summaries used this month
        now = datetime.now(timezone.utc)
        month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        
        summaries_used = db_manager.count_user_summaries(
            user_id=user_id,
            start_date=month_start
        )
        
        if summaries_used >= monthly_limit:
            return False, f"Monthly limit of {monthly_limit} summaries reached for {tier} tier", summaries_used
            
        return True, None, summaries_used
        
    except Exception as e:
        return False, f"Error checking monthly limit: {str(e)}", None
