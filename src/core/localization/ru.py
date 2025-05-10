"""Russian localization messages."""

RU = {
    # Basic messages
    "welcome": "✨ Привет, я *Sumari*\\! Отправь мне ссылку на видео YouTube, и я создам для тебя краткое содержание\\.",
    "select_language": "Пожалуйста, выбери предпочитаемый язык для кратких содержаний:",
    "menu_language_set": "Твой язык установлен на *{language}*\\.",
    # Common words
    "unlimited": "Безлимитно",
    # Error messages
    "security_error": "⚠️ Проверка безопасности не пройдена: {error}",
    "security_check_failed": "⚠️ Ошибка проверки безопасности\\. Пожалуйста, попробуйте снова\\.",
    "blocked_url": "⚠️ Ссылки не на YouTube пока что не поддерживаются \\.",
    "blocked_content": "⚠️ Сообщение содержит заблокированный контент\\.",
    "rate_limit": "⚠️ Достигнут лимит запросов\\. Пожалуйста, подожди минуту перед следующей попыткой\\.",
    "invalid_url": "❌ Неверная ссылка на YouTube\\.",
    "not_youtube_url": "❌ Пожалуйста, отправьте действительную ссылку на видео YouTube\\.",
    "error": "❌ Ошибка: {error}",
    "error_processing": "❌ Ошибка обработки видео: {error}",
    "processing_video": "🎬 *Обработка видео*\n⏱ Примерное время: {eta}",
    # Process messages
    "fetching": "🔍 Получаю субтитры\\.\\.\\.",
    "summarizing": "⏳ Создаю краткое содержание, пожалуйста, подожди\\.\\.\\.",
    "transcript_short": "❌ Текст слишком короткий для создания краткого содержания\\.",
    "no_transcript": "❌ Для этого видео нет субтитров на поддерживаемых языках\\.",
    # Menu messages
    "menu_message": "🎯 *Главное меню*\n\nЧто бы ты хотел сделать\\?",
    "help_message": "🤖 *Доступные команды*\n\n"
    "/start \\- Запустить бота\n"
    "/menu \\- Показать главное меню\n"
    "/help \\- Показать это сообщение\n"
    "/language \\- Изменить язык\n"
    "/preferences \\- Изменить настройки\n\n"
    "ℹ️ *О Sumari*\n\n"
    "Я продвинутый AI\\-бот, который создает краткие содержания видео с YouTube\\. "
    "Используя передовые технологии AI, я анализирую субтитры видео, чтобы извлечь "
    "самую важную информацию\\.\n\n"
    "🎯 *Ключевые особенности*:\n"
    "• Умное создание кратких содержаний с помощью AI\n"
    "• Поддержка множества языков\n"
    "• Настраиваемая длина кратких содержаний\n"
    "• Аудио\\-версии \\(Pro\\)\n"
    "• Быстрая обработка\n\n"
    "💡 *Как это работает*:\n"
    "1\\. Отправь любую ссылку на YouTube\n"
    "2\\. Выбери предпочитаемую длину\n"
    "3\\. Получи краткое содержание за секунды\\!\n\n"
    "🌐 *Языки*:\n"
    "• Интерфейс: Английский, Русский\n"
    "• Краткие содержания: 30\\+ языков\n\n"
    "⭐️ *Премиум\\-функции*:\n"
    "• Больше кратких содержаний в месяц\n"
    "• Приоритетная обработка\n"
    "• Аудио\\-версии\n"
    "• Контроль длины",
    # Account messages
    "account_info": "👤 *Информация об аккаунте*\n\n"
    "• Имя пользователя: *{username}*\n"
    "• Тариф: *{tier}*\n"
    "• Использовано кратких содержаний: *{summaries_used}*\n"
    "• Месячный лимит: *{summaries_limit}*\n"
    "• Уведомления: *{notifications}*",
    # Premium messages
    "premium_features": "🌟 *Премиум\\-планы*\n\n"
    "💫 *Based Plan* \\($5/месяц\\)\n"
    "• 100 кратких содержаний в месяц\n"
    "• Приоритетная обработка\n"
    "• Настройка длины\n\n"
    "🔥 *Pro Plan* \\($20/месяц\\)\n"
    "• Безлимитные краткие содержания\n"
    "• Аудио\\-версии\n"
    "• Приоритетная обработка\n"
    "• Настройка длины\n"
    "• Все будущие функции\n\n"
    "Выбери свой план ниже\\!\n\n"
    "*Твой план*: {tier}\n"
    "*Использовано*: {summaries_used}/{summaries_limit}\n"
    "*Истекает*: {expiry}\n\n"
    "Подписка закончится в дату истечения\\. Возврат средств не производится\\.",
    "premium_based": "💫 *Based Plan*\n\n"
    "• 100 кратких содержаний в месяц\n"
    "• Приоритетная обработка\n"
    "• Настройка длины\n\n"
    "*Твой план*: {tier}\n"
    "*Использовано*: {summaries_used}/{summaries_limit}\n"
    "*Истекает*: {expiry}",
    "premium_pro": "🔥 *Pro Plan*\n\n"
    "• Безлимитные краткие содержания\n"
    "• Аудио\\-версии\n"
    "• Приоритетная обработка\n"
    "• Настройка длины\n"
    "• Все будущие функции\n\n"
    "*Твой план*: {tier}\n"
    "*Использовано*: {summaries_used}/{summaries_limit}\n"
    "*Истекает*: {expiry}",
    # Preferences messages
    "preferences_message": "⚙️ *Настройки*\n\nНастрой параметры кратких содержаний\\:",
    "select_summary_language": "🗣 *Язык кратких содержаний*\n\nВыбери язык для кратких содержаний\\:",
    "summary_preferences": "⚙️ *Настройки кратких содержаний*\n\nВыбери предпочитаемую длину\\:",
    # Summary buttons
    "btn_summary_regenerate": "🔄 Создать новое резюме",
    "btn_summary_voice": "🎧 Прослушать резюме",
    "btn_summary_language": "🌐 Изменить язык",
    # Button texts
    "btn_language": "🌐 Язык",
    "btn_preferences": "⚙️ Настройки",
    "btn_help": "❓ Помощь и информация",
    "btn_premium": "⭐ Премиум",
    "btn_account": "👤 Мой аккаунт",
    # Payment messages
    "payment_method": "💳 *Выбери способ оплаты*\n\n"
    "Выбери, как ты хочешь оплатить подписку:",
    "payment_provider": "🏢 *Выбери платежную систему*\n\n"
    "Выбери предпочитаемую платежную систему:",
    "stripe_checkout": "💳 *Stripe Checkout*\n\n"
    "Нажмите кнопку ниже, чтобы продолжить оплату:\n\n"
    "🔗 *Checkout Link*:\n\n"
    "{url}",
    # Voice messages
    "voice_selection": "🎧 *Настройки аудио*\n\n"
    "Настройте параметры аудио для озвучивания саммари\\. Вы можете включить/выключить аудио, "
    "выбрать пол голоса и язык\\.\n\n"
    "*Текущие настройки*:\n"
    "Аудио: {audio_status}\n"
    "Голос: {voice_gender}\n"
    "Язык: {voice_language}",
    "voice_language": "🌐 *Язык голоса*\n\n" "Выбери язык для синтеза речи:\n\n"
    "Язык голоса: {voice_language}",
    "voice_demo_processing": "🎵 *Обработка демо*\n\n"
    "Создаю аудио\\-пример, пожалуйста, подожди...",
    "voice_demo_ready": "✨ *Демо готово*\n\n" "Вот твой аудио\\-пример! Как звучит?",
    "voice_demo_error": "❌ *Ошибка демо*\n\n"
    "Извини, произошла ошибка при создании аудио\\-примера. "
    "Пожалуйста, попробуй снова.",
    "audio_enabled": "✅ Аудио\\-версии включены",
    "audio_disabled": "❌ Аудио\\-версии отключены",
    # Account buttons
    "btn_transaction_history": "📊 История Транзакций",
    "btn_account_premium": "⭐ Премиум",
    "btn_account_back": "⬅️ Назад в меню",
    "btn_account_notifications": "🔔 Уведомления",
    
    # Language selection messages
    "summary_language_set": "✅ Язык саммари изменен на {language}",
    "already_selected": "Этот язык уже выбран",
    "already_in_menu": "Вы уже находитесь в меню выбора языка",
    "btn_account_delete": "🗑 Удалить аккаунт",
    "btn_notifications_off": "Уведомления Выключены",
    "btn_notifications_on": "Уведомления Включены",
    # Voice buttons
    "btn_voice_male": "👨 Мужской голос",
    "btn_voice_female": "👩 Женский голос",
    "btn_voice_language": "🌐 Язык голоса",
    "btn_voice_back": "⬅️ Назад",
    "btn_audio_toggle": "🔇 Отключить аудио",
    "btn_audio_enable": "🔊 Включить аудио",
    # Payment buttons
    "btn_payment_stripe": "💳 Оплатить через Stripe",
    "btn_payment_crypto": "💎 Оплатить Криптой",
    "btn_payment_back": "⬅️ Назад",
    # Premium buttons
    "btn_premium_based": "💫 Based Plan",
    "btn_premium_pro": "🔥 Pro Plan",
    "btn_premium_back": "⬅️ Назад",
    "btn_premium_extend_pro": "🔄 Продлить Pro",
    "btn_premium_extend_based": "🔄 Продлить Based",
    "btn_premium_upgrade_pro": "🔥 Обновить до Pro ($14)",
    "btn_premium_cancel_subscription": "Отменить",
    "btn_premium_support": "💬 Поддержка",
    "btn_support_chat_bot": "🤖 Чат с ботом",
    "btn_support_community": "👥 Сообщество",
    "btn_support_back": "⬅️ Назад",
    # Preferences buttons
    "btn_pref_summary_length": "📏 Длина",
    "btn_pref_summary_language": "🗣 Язык",
    "btn_pref_voice_settings": "🎧 Настройки голоса",
    "btn_pref_back": "⬅️ Назад",
    "btn_summary_short": "📄 Короткое",
    "btn_summary_medium": "📑 Среднее",
    "btn_summary_detailed": "📚 Подробное",
    # Base buttons
    "btn_back": "⬅️ Назад",
    "btn_cancel": "❌ Отмена",
    # Payment messages
    "payment_method": "💳 *Выбери способ оплаты*\n\n"
    "Выбери, как ты хочешь оплатить подписку:",
    "payment_provider": "🏢 *Выбери платежную систему*\n\n"
    "Выбери предпочитаемую платежную систему:",
    "payment_link": "🔗 *Ссылка для оплаты*\n\n"
    "Нажми на ссылку ниже для завершения оплаты:\n"
    "{url}",
    # Voice messages
    "voice_selection": "🎧 *Настройки аудио*\n\n"
    "Настройте параметры аудио для озвучивания саммари\\. Вы можете включить/выключить аудио, "
    "выбрать пол голоса и язык\\.\n\n"
    "*Текущие настройки*:\n"
    "Аудио: {audio_status}\n"
    "Голос: {voice_gender}\n"
    "Язык: {voice_language}",
    "voice_language": "🌐 *Язык голоса*\n\n" "Выбери язык для синтеза речи:",
    "voice_demo_processing": "🎵 *Обработка демо*\n\n"
    "Создаю аудио\\-пример, пожалуйста, подожди...",
    "voice_demo_ready": "✨ *Демо готово*\n\n" "Вот твой аудио\\-пример! Как звучит?",
    "voice_demo_error": "❌ *Ошибка демо*\n\n"
    "Извини, произошла ошибка при создании аудио\\-примера. "
    "Пожалуйста, попробуй снова.",
    "audio_enabled": "✅ Аудио\\-версии включены",
    "audio_disabled": "❌ Аудио\\-версии отключены",
    # Support messages
    "support_menu": "💬 *Поддержка*\n\nВыбери, как ты хочешь получить помощь:",
    "support_chat_bot": "🤖 *Чат\\-бот поддержки*\n\nЯ здесь, чтобы помочь! Опиши свою проблему или вопрос.",
    "support_community": "👥 *Поддержка сообщества*\n\nПрисоединяйся к нашим каналам:\n• Telegram: @sumari_community\n• Discord: discord.gg/sumari",
    # Subscription cancellation messages
    "cancel_subscription_confirm": "❗ *Отмена подписки*\n\n"
    "Ты уверен, что хочешь отменить подписку\\?\n\n"
    "Твоя подписка будет активна до *{expiry}*\\. "
    "После этого ты потеряешь доступ к премиум\\-функциям\\.\n\n"
    "Хочешь продолжить отмену\\?",
    "btn_confirm_cancel": "Да, отменить",
    "btn_keep_subscription": "✅ Нет, оставить активной",
    "subscription_cancelled": "✅ Твоя подписка отменена\\. "
    "Ты можешь продолжать использовать премиум\\-функции до *{expiry}*\\.",
    "language_changed": "Язык кратких содержаний изменен на *{language}*",
    "length_changed": "Длина кратких содержаний изменена на *{length}*",
    # Summary limit messages
    "summary_limit_reached": " Вы достигли месячного лимита в {limit} конспектов\. Для продолжения использования бота, пожалуйста, обновите свой план\.",
    "summary_limit_warning_free": "⚠️ У вас осталось {remaining} конспектов в этом месяце на бесплатном плане\. Обновите план, чтобы получить больше\!",
    "summary_limit_warning_paid": "⚠️ У вас осталось {remaining} конспектов в этом месяце на плане {tier}\. Рассмотрите возможность обновления, чтобы получить больше\!",
    "summary_limit_near_free": "📊 *Использование*: {used}/{limit} в этом месяце\nОбновите план, чтобы получить больше конспектов\!",
    "summary_limit_near_paid": "📊 *Использование*: {used}/{limit} в этом месяце",
}
