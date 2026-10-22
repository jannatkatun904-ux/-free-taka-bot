import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_TOKEN = os.getenv("GEMINI_TOKEN")

user_data = {}
logging.basicConfig(level=logging.INFO)

def ask_gemini(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    headers = {"Content-Type": "application/json", "X-goog-api-key": GEMINI_TOKEN}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, headers=headers, json=data, timeout=20)
        j = res.json()
        return j['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"AI Error: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("💰 Earn", callback_data='earn')], [InlineKeyboardButton("🤖 Ask AI", callback_data='askai')]]
    await update.message.reply_text(f"Bot Ready!", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'askai':
        await query.edit_message_text("🤖 AI Mode ON! এখন যা খুশি লেখো...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back Menu", callback_data='menu')]]))
    elif query.data == 'menu':
        await start(update, context)

async def handle_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.startswith('/'): return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = ask_gemini(update.message.text)
    await update.message.reply_text(reply[:4000])

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai))
    app.run_polling()

if __name__ == '__main__':
    main()