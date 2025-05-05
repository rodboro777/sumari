# YouTube Summary Bot

A Telegram bot that creates concise summaries of YouTube videos using AI. The bot supports both English and Russian languages and offers customizable summary lengths.

## Features

- 🎥 YouTube video summarization
- 🌐 Multilingual support (English and Russian)
- 📊 Adjustable summary length (short, medium, detailed)
- 📜 Summary history
- 📊 Usage statistics and monitoring
- 🔒 Rate limiting protection
- 💾 Cloud Firestore database
- 💰 Payment integration (planned)

## Project Structure

```
.
├── src/
│   ├── bot/
│   │   └── bot.py           # Main bot logic
│   ├── core/
│   │   ├── keyboards.py     # Telegram keyboard layouts
│   │   ├── localization.py  # Multilingual messages
│   │   └── utils.py         # Helper functions
│   ├── database/
│   │   └── db_manager.py    # Database operations
│   ├── services/
│   │   ├── monitoring.py    # Usage monitoring
│   │   └── video_processor.py # Video processing
│   └── config.py            # Configuration settings
├── data/
│   └── user_data/          # User data storage
├── tests/                  # Test files
├── .env                    # Environment variables
├── .gitignore             # Git ignore rules
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## Database Operations

The bot uses Firebase Cloud Firestore for data persistence. Here's what we store:

### Collections Structure:
- `users/`: User profiles and preferences
  - `{user_id}/`: Individual user documents
    - `history/`: User's summary history
- `api_usage/`: API usage tracking
- `errors/`: Error logging

### Key Operations:
- User Management:
  ```python
  # Add/update user
  db_manager.add_user(user_id)
  
  # Update activity
  db_manager.update_user_activity(user_id)
  ```
- Summary History:
  ```python
  # Add to history
  db_manager.add_to_history(user_id, video_data)
  
  # Get history
  history = db_manager.get_user_history(user_id)
  ```
- Usage Statistics:
  ```python
  # Log API usage
  db_manager.log_api_usage(user_id, api_name, status)
  
  # Get stats
  stats = db_manager.get_user_usage_stats(user_id)
  ```

## Payment Integration (Planned)

The bot will support multiple payment methods:

### Telegram Payments
- Native Telegram Payments API for fiat currencies
- TON payments for cryptocurrency transactions
- Implementation will use Telegram's `PreCheckoutQuery` and `SuccessfulPayment` handlers

### External Payment Methods (Future)
1. Cryptocurrency:
   - TON (Telegram Open Network)
   - Other major cryptocurrencies (BTC, ETH)
   - Integration via crypto payment gateways

2. Stripe Integration:
   - Credit/debit card payments
   - Support for multiple currencies
   - Subscription model support

### Payment Features to Implement:
- Premium subscriptions
- Pay-per-summary model
- Bulk purchase discounts
- Referral rewards
- Custom summary lengths for premium users

To implement payments:
1. Add payment handlers in `bot.py`
2. Create new payment service in `services/payment_processor.py`
3. Add payment tracking in Firestore
4. Implement subscription management
5. Add premium features gating

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-summary-bot.git
cd youtube-summary-bot
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
YOUTUBE_API_KEY=your_youtube_api_key
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json
```

4. Set up Firebase:
   - Create a Firebase project
   - Generate service account credentials
   - Save as `firebase-credentials.json` in project root
   - Enable Firestore in your Firebase console

5. Run the bot:
```bash
python src/bot/bot.py
```

## Usage

1. Start the bot in Telegram: `/start`
2. Send a YouTube video URL
3. Choose your preferred summary length
4. Get your video summary!

## Available Commands

- `/start` - Start the bot
- `/menu` - Show main menu
- `/language` - Change language
- `/preferences` - Change summary preferences
- `/history` - View summary history
- `/help` - Show help message
- `/about` - About the bot

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 