import logging
import os
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# =========== 2 টা টোকেন এখানে বসা ===========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
# ============================================

# AI সেটআপ
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

user_data = {}
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.first_name
    if len(context.args) > 0:
        referrer_id = context.args[0]
        try:
            ref_id = int(referrer_id)
            if ref_id != user_id and ref_id in user_data:
                user_data[ref_id]['balance'] = user_data[ref_id].get('balance', 0) + 10
                await context.bot.send_message(chat_id=ref_id, text=f"Congrats! {username} joined with your link. You got 10 Taka bonus!")
        except: pass
    if user_id not in user_data:
        user_data[user_id] = {'balance': 0, 'referrals': 0}
    keyboard = [
        [InlineKeyboardButton("💰 Earn", callback_data='earn')],
        [InlineKeyboardButton("👥 Refer", callback_data='refer'), InlineKeyboardButton("💳 Balance", callback_data='balance')],
        [InlineKeyboardButton("💸 Withdraw", callback_data='withdraw')],
        [InlineKeyboardButton("🤖 Ask AI", callback_data='askai')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"Assalamu Alaikum {username}!\n\nWelcome to Free Taka Earn Bot\n\nEarn daily + এখন AI ও আছে!\nযেকোনো প্রশ্ন লিখলেই AI উত্তর দেবে।\n\nClick below to start:"
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {'balance': 0, 'referrals': 0}

    if query.data == 'earn':
        user_data[user_id]['balance'] += 2
        keyboard = [[InlineKeyboardButton("✅ Earn More", callback_data='earn')], [InlineKeyboardButton("Back Menu", callback_data='menu')]]
        await query.edit_message_text(f"Task Done!\nYou got 2 Taka!\nCurrent Balance: {user_data[user_id]['balance']} Taka", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == 'refer':
        bot_username = (await context.bot.get_me()).username
        refer_link = f"https://t.me/{bot_username}?start={user_id}"
        keyboard = [[InlineKeyboardButton("Back Menu", callback_data='menu')]]
        await query.edit_message_text(f"Refer and Earn!\n\nYour Refer Link:\n{refer_link}\n\nPer Refer you get 10 Taka!", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == 'balance':
        keyboard = [[InlineKeyboardButton("Back Menu", callback_data='menu')]]
        await query.edit_message_text(f"Your Balance\n\nTotal: {user_data[user_id]['balance']} Taka\nMinimum Withdraw: 100 Taka", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == 'withdraw':
        bal = user_data[user_id]['balance']
        if bal >= 100:
            keyboard = [[InlineKeyboardButton("Back Menu", callback_data='menu')]]
            await query.edit_message_text(f"Withdraw Request Sent!\nAmount: {bal} Taka\nYou will get payment in 24h.", reply_markup=InlineKeyboardMarkup(keyboard))
            user_data[user_id]['balance'] = 0
        else:
            keyboard = [[InlineKeyboardButton("Refer", callback_data='refer'), InlineKeyboardButton("Back Menu", callback_data='menu')]]
            await query.edit_message_text(f"Low Balance!\nYou have: {bal} Taka\nNeed: 100 Taka\nDo more tasks!", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == 'askai':
        keyboard = [[InlineKeyboardButton("Back Menu", callback_data='menu')]]
        await query.edit_message_text(f"🤖 AI Mode ON!\n\nএখন যা খুশি লেখো, আমি AI দিয়ে উত্তর দেবো।\nযেমন: `বাংলাদেশ নিয়ে রচনা লেখো`", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == 'menu':
        await start(update, context)

# === নতুন AI ফাংশন ===
async def handle_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.startswith('/'): return
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text[:4000])
    except Exception as e:
        await update.message.reply_text(f"AI Error: {e}\n\nনতুন API Key টা ঠিকমতো বসিয়েছো তো?")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai))
    print("Bot is running with AI...")
    app.run_polling()

if __name__ == '__main__':
    main()