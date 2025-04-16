import os
import logging
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont
import ctypes
import tempfile

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found!")
        return None
    except json.JSONDecodeError:
        logger.error("Invalid config.json format!")
        return None

config = load_config()
if not config:
    raise SystemExit("Failed to load configuration!")

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Hi! Send me an image (.png, .jpg, .jpeg, .gif) and I\'ll set it on @YOURUSENAME's computer.\n"
        "Note: For .gif files, only the first frame will be used as the wallpaper."
    )

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban a user from using the bot."""
    if update.effective_user.id != config['admin_chat_id']:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    
    if not context.args:
        await update.message.reply_text("Please provide a ChatID to ban.")
        return
    
    try:
        user_id = int(context.args[0])
        if user_id not in config['banned_users']:
            config['banned_users'].append(user_id)
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            await update.message.reply_text(f"ChatID {user_id} has been banned.")
        else:
            await update.message.reply_text(f"ChatID {user_id} is already banned.")
    except ValueError:
        await update.message.reply_text("Invalid ChatID. Please provide a ChatID.")

def add_watermark(image, username, chat_id):
    """Add watermark to the image."""
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    watermark = f"@{username} ({chat_id})"
    text_bbox = draw.textbbox((0, 0), watermark, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = ((image.width - text_width) // 2, (image.height - text_height) // 2)
    draw.text(position, watermark, font=font, fill=(255, 255, 255, 128))
    return image

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming images."""
    user_id = update.effective_user.id
    if user_id in config['banned_users']:
        await update.message.reply_text("You have been banned from using this bot.")
        return
    file = await context.bot.get_file(update.message.photo[-1].file_id)
    file_extension = os.path.splitext(file.file_path)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        await update.message.reply_text(
            "Invalid file format. Please send a .png, .jpg, .jpeg, or .gif file."
        )
        return
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, f"wallpaper{file_extension}")
            await file.download_to_drive(file_path)
            with Image.open(file_path) as img:
                if file_extension == '.gif':
                    img = img.convert('RGB')
                watermarked_img = add_watermark(
                    img,
                    update.effective_user.username or "unknown",
                    update.effective_chat.id
                )
                watermarked_path = os.path.join(temp_dir, f"wallpaper_watermarked{file_extension}")
                watermarked_img.save(watermarked_path)
                if os.name == 'nt':  
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, watermarked_path, 0)
                    await update.message.reply_text("Wallpaper has been changed successfully!")
                else:
                    await update.message.reply_text("Wallpaper setting is only supported on Windows.")
                    return
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        await update.message.reply_text("Sorry, there was an error processing your image.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming documents."""
    user_id = update.effective_user.id
    if user_id in config['banned_users']:
        await update.message.reply_text("You have been banned from using this bot.")
        return
    document = update.message.document
    file_extension = os.path.splitext(document.file_name)[1].lower()
    
    if file_extension not in ALLOWED_EXTENSIONS:
        await update.message.reply_text(
            "Invalid file format. Please send a .png, .jpg, .jpeg, or .gif file."
        )
        return 
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, f"wallpaper{file_extension}")
            await document.get_file().download_to_drive(file_path)            
            with Image.open(file_path) as img:
                if file_extension == '.gif':
                    img = img.convert('RGB')
                watermarked_img = add_watermark(
                    img,
                    update.effective_user.username or "unknown",
                    update.effective_chat.id
                )
                watermarked_path = os.path.join(temp_dir, f"wallpaper_watermarked{file_extension}")
                watermarked_img.save(watermarked_path)
                if os.name == 'nt':
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, watermarked_path, 0)
                    await update.message.reply_text("Wallpaper has been changed successfully!")
                else:
                    await update.message.reply_text("Wallpaper setting is only supported on Windows.")
                    return
                
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        await update.message.reply_text("Sorry, there was an error processing your file.")

def main():
    """Start the bot."""
    if not config['bot_token']:
        logger.error("No bot token found in config.json!")
        return
    application = Application.builder().token(config['bot_token']).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.run_polling()

if __name__ == '__main__':
    main() 