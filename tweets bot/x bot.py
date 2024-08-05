from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from typing import final
from io import BytesIO
from PIL import Image
import pyppeteer
import asyncio

KEY: final = 'YOUR-API-KEY'
bot_username: final = 'YOUR_BOT_NAME'


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello There. I am a bot that converts a Twitter link into a photo.')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Just send me a Twitter link and I will convert it into a photo.')


# Function to capture a screenshot


async def capture_screenshot(url):
    try:
        browser = await pyppeteer.launch(headless=True, executablePath='C:/Users/nar7g/AppData/Local/Programs/Opera/opera.exe')  # Update this path to your Opera installation
        page = await browser.newPage()
        await page.goto(url, {'waitUntil': 'networkidle2'})
        screenshot = await page.screenshot()
        await browser.close()
        return screenshot
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return None


# Responses
def handle_responses(text: str) -> str:
    if 'https://x.com/' in text.lower():
        return text
    else:
        return 'This is not a valid Twitter link. Please try again.'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.username}) in {message_type}: {text}')

    if message_type == 'group':
        if bot_username in text:
            new_text: str = text.replace(bot_username, '').strip()
            response: str = handle_responses(new_text)
        else:
            return
    else:
        response: str = handle_responses(text)

    if response.startswith('https://'):
        screenshot = await capture_screenshot(response)
        if screenshot:
            image = Image.open(BytesIO(screenshot))
            bio = BytesIO()
            bio.name = 'screenshot.png'
            image.save(bio, 'PNG')
            bio.seek(0)
            await update.message.reply_photo(photo=bio)
        else:
            await update.message.reply_text('Failed to capture screenshot.')
    else:
        await update.message.reply_text(response)


async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update "{update}" caused error "{context.error}"')

if __name__ == '__main__':
    print('Starting the bot...')
    app = Application.builder().token(KEY).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(handle_error)

    # Polls the bot
    print('Polling...')
    asyncio.run(app.run_polling(poll_interval=1))