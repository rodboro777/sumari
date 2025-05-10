"""Utilities for calculating and formatting estimated processing times."""

def calculate_eta(content_length: int) -> float:
    """Calculate estimated processing time based on content length.
    
    Args:
        content_length: Length of the content in characters
        
    Returns:
        Estimated processing time in seconds
    """
    # Base time: 2 seconds
    # Additional time: 0.1 seconds per 1000 characters
    eta_seconds = 2 + (content_length / 1000 * 0.1)
    # Ensure minimum of 3 seconds
    return max(3, eta_seconds)

def format_eta(eta_seconds: float) -> str:
    """Format estimated processing time in a user-friendly way.
    
    Args:
        eta_seconds: Estimated processing time in seconds
        
    Returns:
        Formatted ETA string (e.g., "3 seconds" or "1 minute 30 seconds")
    """
    if eta_seconds < 60:
        return f"{int(eta_seconds)} seconds"
    else:
        minutes = int(eta_seconds / 60)
        remaining_seconds = int(eta_seconds % 60)
        return f"{minutes} minutes {remaining_seconds} seconds"
