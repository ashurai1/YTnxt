import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters
from handlers.link_handler import handle_message, handle_start
from handlers.button_handler import handle_button

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Simple HTTP server for Render Health Check
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN environment variable not set.")
        return

    if not os.path.exists('temp'):
        os.makedirs('temp')

    # Start Health Check in a separate thread
    threading.Thread(target=run_health_check, daemon=True).start()

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_button))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
