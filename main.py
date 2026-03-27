import os
import logging
import nest_asyncio
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters
from handlers.link_handler import handle_message, handle_start
from handlers.button_handler import handle_button

nest_asyncio.apply()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN environment variable not set.")
        return

    if not os.path.exists('temp'):
        os.makedirs('temp')

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_button))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
