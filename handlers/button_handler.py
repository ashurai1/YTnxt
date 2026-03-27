import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import NetworkError, TimedOut
from utils.downloader import download_video

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if not data.startswith("dl_"):
        return
        
    resolution_str = data.split("_")[1]
    height = int(resolution_str.replace("p", ""))
    
    url = context.user_data.get('current_url')
    if not url:
        await query.edit_message_text("❌ Session expired. Please send the link again.")
        return
        
    await query.edit_message_text(
        f"⚡️ *Initializing Download...*\n"
        f"📹 Quality: `{resolution_str}`\n"
        f"⏳ Please wait, this might take a few minutes...\n\n"
        f"🔄 *Powered by Ashwani Bot*",
        parse_mode='Markdown'
    )
    
    file_path = None
    try:
        file_path = await download_video(url, height)
        
        await query.edit_message_text(
            f"✅ *Download Complete!*\n"
            f"🚀 Uploading to Telegram... Please hold tight!",
            parse_mode='Markdown'
        )
        
        if os.path.exists(file_path):
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > 50:
                await query.edit_message_text(
                    f"⚠️ *File Too Large!*\n"
                    f"📦 Size: `{file_size_mb:.1f} MB` (Telegram limit: 50MB)\n"
                    f"💡 Try selecting a *lower quality* option.",
                    parse_mode='Markdown'
                )
            else:
                with open(file_path, 'rb') as video:
                    await context.bot.send_video(
                        chat_id=update.effective_chat.id,
                        video=video,
                        caption=(
                            f"🎬 *Downloaded in {resolution_str}*\n"
                            f"━━━━━━━━━━━━━━━━━\n"
                            f"✨ *Made by Ashwani Bot*\n"
                            f"🤖 @YTnxtBot | Fast & Free"
                        ),
                        supports_streaming=True,
                        read_timeout=120,
                        write_timeout=120
                    )
                await query.delete_message()
        else:
            await query.edit_message_text("❌ Downloaded file not found.")
            
    except (NetworkError, TimedOut):
        await query.edit_message_text(
            "⏱️ *Upload Timeout!*\n"
            "📦 The file might be too large for Telegram.\n"
            "💡 Try a lower quality option.",
            parse_mode='Markdown'
        )
    except Exception as e:
        await query.edit_message_text(
            "❌ *Something went wrong!*\n"
            "🔁 Please try again or choose a different quality.",
            parse_mode='Markdown'
        )
        print(f"Error downloading/uploading: {e}")
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting temp file: {e}")
