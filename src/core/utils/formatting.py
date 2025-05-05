"""Text formatting utilities."""

from datetime import datetime
from typing import Dict, Optional


def format_summary_for_telegram(text: str) -> str:
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


def format_expiry_date(expiry_date: Optional[str], language: str = "en") -> str:
    """Format expiry date based on language."""
    if not expiry_date:
        return "∞"
        
    try:
        expiry_dt = datetime.fromisoformat(expiry_date)
        if language == "ru":
            months = [
                "", "Янв", "Фев", "Мар", "Апр", "Май", "Июн",
                "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"
            ]
            return f"{expiry_dt.day} {months[expiry_dt.month]} {expiry_dt.year}"
        else:
            return expiry_dt.strftime("%d %b %Y")
    except Exception:
        return expiry_date


def format_premium_status(status: Dict, language: str) -> str:
    """Format premium status message."""
    from src.core.localization import get_message  # Import here to avoid circular imports
    
    tier = status.get("tier", "free")
    summaries_used = status.get("summaries_used", 0)
    summaries_limit = status.get("summaries_limit", 3)
    expiry_date = status.get("expiry_date")
    
    if tier == "pro":
        message = get_message("premium_pro", language)
    elif tier == "based":
        message = get_message("premium_based", language)
    else:
        message = get_message("premium_features", language)
    
    return message.format(
        tier=tier.upper(),
        summaries_used=summaries_used,
        summaries_limit="∞" if summaries_limit == -1 else str(summaries_limit),
        expiry=format_expiry_date(expiry_date, language)
    )
