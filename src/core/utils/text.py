"""Text formatting utilities."""

from telegram.helpers import escape_markdown


def escape_md(text: str) -> str:
    """
    Escape Markdown V2 special characters in text using telegram's helper.

    Args:
        text (str): Text to escape

    Returns:
        str: Escaped text safe for MarkdownV2 formatting
    """
    try:
        return escape_markdown(str(text), version=2)
    except Exception:
        # Fallback to removing markdown entirely if escaping fails
        return (
            str(text)
            .replace("*", "")
            .replace("_", "")
            .replace("`", "")
            .replace("[", "")
            .replace("]", "")
        )


def format_md(text: str, is_bold: bool = False) -> str:
    """
    Format text with Markdown V2 and escape special characters.

    Args:
        text (str): Text to format
        is_bold (bool): Whether to make the text bold

    Returns:
        str: Formatted and escaped text
    """
    escaped = escape_md(str(text))
    return f"*{escaped}*" if is_bold else escaped


def to_html(text: str) -> str:
    """
    Convert text to HTML format, escaping special characters.

    Args:
        text (str): Text to convert

    Returns:
        str: HTML-formatted text
    """
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
