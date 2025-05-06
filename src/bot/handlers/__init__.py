"""
Bot handlers package.

Bot command and callback handlers.
"""

from .basic import (
    start,
    menu_command,
    help_command,
    about_command,
    set_language,
    button_callback,
    test_voice,
    test_tts,
)

from .account import handle_account

from .premium import (
    handle_premium as premium_command,
    handle_support_menu,
    handle_cancel_subscription_confirm,
    handle_cancel_subscription,
)

from .preferences import (
    handle_preferences,
    handle_summary_language,
    handle_audio_settings,
    handle_length_setting,
)

from .audio import handle_audio_summary

__all__ = [
    # Command handlers
    'start',
    'menu_command',
    'help_command',
    'about_command',
    'set_language',
    'button_callback',
    'test_voice',
    'test_tts',
    
    # Module handlers
    'handle_account',
    'handle_preferences',
    'handle_summary_language',
    'handle_audio_settings',
    'handle_length_setting',
    'handle_premium',
    'handle_audio_summary',
]
