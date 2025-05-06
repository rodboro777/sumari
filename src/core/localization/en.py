"""English localization messages."""

EN = {
    # Basic messages
    "welcome": "✨ Hi, I'm *Sumari*\\! Send me a YouTube video link, and I'll create a summary for you\\.",
    "select_language": "🌐 *Language Selection*\n\nPlease select your preferred language for summaries:",
    "language_set": "Your language has been set to *{language}*\\. Summaries will be in this language, you can change sumamry language in the preferences\\.",
    # Common words
    "unlimited": "Unlimited",
    # Error messages
    "rate_limit": "⚠️ You've reached the request limit\\. Please wait a minute before trying again\\.",
    "invalid_url": "❌ Invalid YouTube URL\\.",
    "error": "❌ Error: {error}",
    # Process messages
    "fetching": "🔍 Fetching transcript\\.\\.\\.",
    "summarizing": "⏳ Summarizing, please wait\\.\\.\\.",
    "transcript_short": "❌ Transcript too short to summarize\\.",
    "no_transcript": "❌ No transcript available for this video in the supported languages\\.",
    # Menu messages
    "menu_message": "🎯 *Main Menu*\n\nWhat would you like to do?",
    "help_message": "🤖 *Available Commands*\n\n"
    "/start \\- Start the bot\n"
    "/menu \\- Show main menu\n"
    "/help \\- Show this help message\n"
    "/language \\- Change language\n"
    "/preferences \\- Change summary preferences\n\n"
    "ℹ️ *About Sumari*\n\n"
    "I'm an advanced AI bot that creates concise summaries of YouTube videos\\. "
    "Using cutting\\-edge AI technology, I analyze video transcripts to extract "
    "the most important information\\.\n\n"
    "🎯 *Key Features*:\n"
    "• Smart summarization using AI\n"
    "• Support for multiple languages\n"
    "• Customizable summary length\n"
    "• Audio summaries \\(Pro\\)\n"
    "• Fast processing\n\n"
    "💡 *How it Works*:\n"
    "1\\. Send any YouTube video link\n"
    "2\\. Choose your preferred length\n"
    "3\\. Get your summary in seconds\\!\n\n"
    "🌐 *Languages*:\n"
    "• Interface: English, Russian\n"
    "• Summaries: 30\\+ languages\n\n"
    "⭐️ *Premium Features*:\n"
    "• More summaries per month\n"
    "• Priority processing\n"
    "• Audio summaries\n"
    "• Custom length control",
    # Account messages
    "account_info": "👤 *Account Information*\n\n"
    "• Username: *@{username}*\n"
    "• Tier: *{tier}*\n"
    "• Summaries: *{summaries_used}*/*{summaries_limit}*",
    # Premium messages
    "premium_features": "🌟 *Premium Plans*\n\n"
    "💫 *Based Plan* \\($5/month\\)\n"
    "• 100 summaries per month\n"
    "• Priority processing\n"
    "• Custom summary length\n\n"
    "⭐️ *Pro Plan* \\($20/month\\)\n"
    "• Unlimited summaries\n"
    "• Audio summaries\n"
    "• Priority processing\n"
    "• Custom summary length\n"
    "• All future features\n\n"
    "Choose your plan below\\!\n\n"
    "*Your Plan*: {tier}\n"
    "*Summaries Used*: {summaries_used}/{summaries_limit}\n"
    "*Expires*: {expiry}\n\n"
    "Your subscription will end on the expiration date\\. No refunds will occur\\.",
    "premium_based": "💫 *Based Plan*\n\n"
    "• 100 summaries per month\n"
    "• Priority processing\n"
    "• Custom summary length\n\n"
    "*Your Plan*: {tier}\n"
    "*Summaries Used*: {summaries_used}/{summaries_limit}\n"
    "*Expires*: {expiry}",
    "premium_pro": "⭐️ *Pro Plan*\n\n"
    "• Unlimited summaries\n"
    "• Audio summaries\n"
    "• Priority processing\n"
    "• Custom summary length\n"
    "• All future features\n\n"
    "*Your Plan*: {tier}\n"
    "*Summaries Used*: {summaries_used}/{summaries_limit}\n"
    "*Expires*: {expiry}",
    # Preferences messages
    "preferences_message": "⚙️ *Preferences*\n\nCustomize your summary settings:",
    "select_summary_language": "🗣 *Summary Language*\n\nChoose the language for your summaries:",
    "summary_preferences": "⚙️ *Summary Preferences*\n\nChoose your preferred summary length:",
    # Button texts
    "btn_language": "🌐 Language",
    "btn_preferences": "⚙️ Preferences",
    "btn_help": "❓ Help & About",
    "btn_premium": "⭐ Premium",
    "btn_account": "👤 My Account",
    # Account buttons
    "btn_account_history": "📊 History",
    "btn_account_premium": "⭐ Premium",
    "btn_account_back": "⬅️ Back to Menu",
    "btn_account_notifications": "🔔 Notifications",
    "stripe_checkout": "💳 *Stripe Checkout*\n\n"
    "Click the button below to proceed with the payment:\n\n"
    "🔗 *Checkout Link*:\n\n"
    "{url}",
    "btn_account_delete": "🗑 Delete Account",
    # Voice buttons
    "btn_voice_male": "👨 Male Voice",
    "btn_voice_female": "👩 Female Voice",
    "btn_voice_language": "🌐 Voice Language",
    "btn_voice_back": "⬅️ Back",
    "btn_audio_toggle": "🔇 Disable Audio",
    "btn_audio_enable": "🔊 Enable Audio",
    # Payment buttons
    "btn_payment_stripe": "💳 Pay with Stripe",
    "btn_payment_crypto": "💎 Pay with Crypto",
    "btn_payment_back": "⬅️ Back",
    # Premium buttons
    "btn_premium_based": "💫 Based Plan",
    "btn_premium_pro": "⭐️ Pro Plan",
    "btn_premium_back": "⬅️ Back",
    "btn_premium_extend_pro": "🔄 Renew Pro",
    "btn_premium_extend_based": "🔄 Renew Based",
    "btn_premium_upgrade_pro": "⭐ Upgrade to Pro",
    "btn_premium_cancel_subscription": "Cancel",
    "btn_premium_support": "💬 Support",
    "btn_support_chat_bot": "🤖 Chat with Bot",
    "btn_support_community": "👥 Community",
    "btn_support_back": "⬅️ Back",
    # Preferences buttons
    "btn_pref_summary_length": "📏 Summary Length",
    "btn_pref_summary_language": "🗣 Summary Language",
    "btn_pref_voice_settings": "🎧 Voice Settings",
    "btn_pref_back": "⬅️ Back",
    "btn_summary_short": "📄 Short",
    "btn_summary_medium": "📑 Medium",
    "btn_summary_detailed": "📚 Detailed",
    # Summary buttons
    "btn_summary_regenerate": "🔄 Regenerate Summary",
    "btn_summary_voice": "🎧 Listen to Summary",
    "btn_summary_language": "🌐 Change Language",
    # Base buttons
    "btn_back": "⬅️ Back",
    "btn_cancel": "❌ Cancel",
    # Payment messages
    "payment_method": "💳 *Choose Payment Method*\n\n"
    "Select how you would like to pay for your subscription:",
    "payment_provider": "🏢 *Select Payment Provider*\n\n"
    "Choose your preferred payment provider:",
    "payment_link": "🔗 *Payment Link*\n\n"
    "Click the link below to complete your payment:\n"
    "🔗 Checkout URL",
    # Voice messages
    "voice_selection": "🎧 *Audio Settings*\n\n"
    "Configure your audio preferences for summaries\\. You can enable/disable audio, "
    "choose voice gender, and select language\\.\n\n"
    "Current Settings:\n\n"
    "• Audio: {audio_status}\n"
    "• Voice: {voice_gender}\n"
    "• Language: {voice_language}",
    "voice_language": "🌐 *Voice Language*\n\n"
    "Select the language for voice synthesis:",
    "voice_demo_processing": "🎵 *Processing Demo*\n\n"
    "Creating your audio sample, please wait\\.\\.\\.",
    "voice_demo_ready": "✨ *Demo Ready*\n\n"
    "Here's your audio sample\\! How does it sound?",
    "voice_demo_error": "❌ *Demo Error*\n\n"
    "Sorry, there was an error creating your audio sample\\. "
    "Please try again\\.",
    "audio_enabled": "✅ Audio summaries are enabled",
    "audio_disabled": "❌ Audio summaries are disabled",
    # Support messages
    "support_menu": "💬 *Support*\n\nChoose how you would like to get help:",
    "support_chat_bot": "🤖 *Chat Bot Support*\n\nI'm here to help\\! Please describe your issue or question\\.",
    "support_community": "👥 *Community Support*\n\nJoin our community channels:\n• Telegram: @sumari\\_community\n• Discord: discord\\.gg/sumari",
    # Subscription cancellation messages
    "cancel_subscription_confirm": "❗ *Cancel Subscription*\n\n"
    "Are you sure you want to cancel your subscription?\n\n"
    "Your subscription will remain active until *{expiry}*\\. "
    "After that, you'll lose access to premium features\\.\n\n"
    "Would you like to proceed with cancellation?",
    "btn_confirm_cancel": "Yes, Cancel",
    "btn_keep_subscription": "✅ No, Keep Active",
    "subscription_cancelled": "✅ Your subscription has been cancelled\\. "
    "You can continue using premium features until *{expiry}*\\.",
    "language_changed": "Summary language changed to *{language}*",
    "length_changed": "Summary length changed to *{length}*",
}
