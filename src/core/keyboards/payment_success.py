
from telegram import InlineKeyboardMarkup
from src.core.keyboards.menu import create_keyboard
from src.core.localization import get_message


class PaymentSuccessKeyboard:
    """Keyboard for payment success message."""

    @staticmethod
    def get_keyboard(language: str) -> InlineKeyboardMarkup:
        """Get the keyboard with back to menu and account buttons."""
        buttons = [
            [
                {
                    "text": get_message("btn_back_to_menu", language),
                    "callback_data": "back_to_menu",
                },
                {
                    "text": get_message("btn_my_account", language),
                    "callback_data": "show_account",
                }
            ]
        ]
        return create_keyboard(buttons, language)

    @staticmethod
    def get_success_message(language: str) -> str:
        """Get the success message with proper markdown escaping."""
        return (
            "🎉 *" + get_message("payment_successful", language) + "\!*\n\n" +
            get_message("premium_features_active", language)
        )
