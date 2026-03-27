from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.validator import is_valid_youtube_url
from utils.downloader import get_video_info, get_available_resolutions

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "🤖 *Welcome to Ashwani Bot!*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🎬 *Your Personal YouTube Downloader*\n\n"
        "📌 *How to use:*\n"
        "  1️⃣ Paste a YouTube link\n"
        "  2️⃣ Pick your quality (up to 1080p)\n"
        "  3️⃣ Get your video instantly!\n\n"
        "⚡️ Fast • 🆓 Free • 🔒 Private\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✨ *Made by Ashwani Bot*"
    )
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if not text:
        return
        
    if not is_valid_youtube_url(text):
        await update.message.reply_text(
            "❌ *Invalid YouTube URL!*\n"
            "🔗 Please send a valid YouTube link.",
            parse_mode='Markdown'
        )
        return
        
    processing_msg = await update.message.reply_text(
        "🔍 *Fetching video info...*\n"
        "⚡️ _Powered by Ashwani Bot_",
        parse_mode='Markdown'
    )
    
    try:
        info = await get_video_info(text)
        resolutions = get_available_resolutions(info)
        
        if not resolutions:
            await processing_msg.edit_text(
                "⚠️ *No downloadable formats found!*\n"
                "😔 This video might be unavailable or restricted.",
                parse_mode='Markdown'
            )
            return
            
        context.user_data['current_url'] = text
        
        keyboard = []
        row = []
        for i, res in enumerate(resolutions):
            row.append(InlineKeyboardButton(res, callback_data=f"dl_{res}"))
            if len(row) == 2 or i == len(resolutions) - 1:
                keyboard.append(row)
                row = []
                
        reply_markup = InlineKeyboardMarkup(keyboard)
        title = info.get('title', 'Video')
        duration = info.get('duration', 0)
        mins, secs = divmod(duration, 60)
        
        await processing_msg.edit_text(
            f"🎬 *{title}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏱ Duration: `{mins}:{secs:02d}`\n"
            f"📥 *Select Quality:*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await processing_msg.edit_text(
            "❌ *Error fetching video!*\n"
            "🔁 Please try again with a valid YouTube link.",
            parse_mode='Markdown'
        )
        print(f"Error fetching info: {e}")
