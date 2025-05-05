# Localized messages
MESSAGES = {
    "en": {
        "welcome": "🎬 Send a YouTube URL. I will get the transcript and summarize it.\n\nUse /language to select your preferred language for summaries.",
        "select_language": "Please select your preferred language for summaries:",
        "language_set": "Your language has been set to {}, summaries will be in this language",
        "rate_limit": "⚠️ You've reached the request limit. Please wait a minute before trying again.",
        "invalid_url": "❌ Invalid YouTube URL.",
        "fetching": "🔍 Fetching transcript...",
        "transcript_short": "❌ Transcript too short to summarize.",
        "summarizing": "⏳ Summarizing, please wait...",
        "api_limit": "⚠️ The AI service is currently overloaded or we've hit the API quota limit. Please try again later.",
        "summarization_error": "❌ Error during summarization: {}",
        "no_transcript": "❌ No transcript available for this video in the supported languages.",
        "error": "❌ Error: {}",
        "summary_header": "✅ Summary:\n\n",
        "help_message": "🤖 *Available Commands*:\n\n"
        "/start - Start the bot\n"
        "/menu - Show main menu\n"
        "/help - Show this help message\n"
        "/language - Change language\n"
        "/preferences - Change summary preferences",
        "about_message": "📝 *YouTube Summary Bot*\n\n"
        "This bot helps you get summaries of YouTube videos.\n"
        "Just send a YouTube URL and I'll create a summary for you!",
        "menu_message": "🎯 *Main Menu*\n\nWhat would you like to do?",
        "video_preview": "📺 *Video Details*:\n\nTitle: *{}*\nChannel: {}\nDuration: {}\n\nWould you like me to summarize this video?",
        "summary_preferences": "⚙️ *Summary Preferences*\n\nChoose your preferred summary length:",
        "summary_length_short": "Short (key points)",
        "summary_length_medium": "Medium (balanced)",
        "summary_length_detailed": "Detailed (comprehensive)",
        "preferences_saved": "✅ Preferences saved!\n\nCurrent settings:\n• Length: *{}*\n\nFuture summaries will use these settings.",
        "current_settings": "⚙️ *Current Settings*\n\n• Language: *{}*\n• Summary Length: *{}*",
    },
    "ru": {
        "welcome": "🎬 Отправьте ссылку на YouTube. Я получу стенограмму и сделаю резюме.\n\nИспользуйте /language чтобы выбрать предпочитаемый язык для резюме.",
        "select_language": "Пожалуйста, выберите предпочитаемый язык для резюме:",
        "language_set": "Ваш язык установлен на {}, ответы будут на этом языке",
        "rate_limit": "⚠️ Вы достигли лимита запросов. Пожалуйста, подождите минуту перед повторной попыткой.",
        "invalid_url": "❌ Неверная ссылка на YouTube.",
        "fetching": "🔍 Получение стенограммы...",
        "transcript_short": "❌ Стенограмма слишком короткая для резюме.",
        "summarizing": "⏳ Создание резюме, пожалуйста, подождите...",
        "api_limit": "⚠️ Сервис ИИ в настоящее время перегружен или мы достигли лимита API. Пожалуйста, повторите попытку позже.",
        "summarization_error": "❌ Ошибка при создании резюме: {}",
        "no_transcript": "❌ Для этого видео нет доступной стенограммы на поддерживаемых языках.",
        "error": "❌ Ошибка: {}",
        "summary_header": "✅ Резюме:\n\n",
        "help_message": "🤖 *Доступные команды*:\n\n"
        "/start - Запустить бота\n"
        "/menu - Показать главное меню\n"
        "/help - Показать это сообщение\n"
        "/language - Изменить язык\n"
        "/preferences - Изменить настройки саммари",
        "about_message": "📝 *Бот для саммари YouTube*\n\n"
        "Этот бот помогает получить краткое содержание YouTube видео.\n"
        "Просто отправьте ссылку на YouTube, и я создам саммари!",
        "menu_message": "🎯 *Главное меню*\n\nЧто бы вы хотели сделать?",
        "video_preview": "📺 *Информация о видео*:\n\nНазвание: *{}*\nКанал: {}\nДлительность: {}\n\nХотите получить краткое содержание этого видео?",
        "summary_preferences": "⚙️ *Настройки краткого содержания*\n\nВыберите  длину саммари:",
        "summary_length_short": "Короткое (основные моменты)",
        "summary_length_medium": "Среднее (сбалансированное)",
        "summary_length_detailed": "Подробное (всестороннее)",
        "preferences_saved": "✅ Настройки сохранены!\n\nТекущие настройки:\n• Длина: *{}*\n\nБудущие саммари будут использовать эти настройки.",
        "current_settings": "⚙️ *Текущие настройки*\n\n• Язык: *{}*\n• Длина саммари: *{}*",
    },
}


def get_message(key, user_id, user_preferences):
    """Get localized message based on user language preference"""
    lang = user_preferences.get(user_id, {}).get("language", "en")
    return MESSAGES[lang][key]
