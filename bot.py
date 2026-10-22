import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_TOKEN = os.getenv("GEMINI_TOKEN")

ADMIN_ID = 8003993365
ADMIN_PASSWORD = "Raihan01@#@"

user_data = {}
admin_auth = {}
logging.basicConfig(level=logging.INFO)

def ask_gemini(prompt):
    try:
        if not GEMINI_TOKEN:
            return "❌ GEMINI_TOKEN Render এ বসানো নেই"
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {"Content-Type": "application/json", "X-goog-api-key": GEMINI_TOKEN}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, headers=headers, json=data, timeout=20)
        j = r.json()
        if 'candidates' not in j:
            return "❌ Gemini Token Expire! aistudio.google.com/app/apikey থেকে নতুন AIza... Key নিয়ে GEMINI_TOKEN এ বসাও"
        return j['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"AI Error: {e}"

async def get_main_menu(uid):
    kb = [
        [InlineKeyboardButton("💰 Earn", callback_data='earn')],
        [InlineKeyboardButton("🤖 Ask AI", callback_data='askai')]
    ]
    if uid == ADMIN_ID:
        kb.append([InlineKeyboardButton("🔐 Admin Panel", callback_data='admin_panel')])
    return kb

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_data:
        user_data[uid] = {'balance': 0, 'name': update.effective_user.first_name}
    kb = await get_main_menu(uid)
    await update.message.reply_text("Bot Ready! ✅ Admin Fixed", reply_markup=InlineKeyboardMarkup(kb))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    data = q.data

    if data == 'admin_panel':
        if uid != ADMIN_ID:
            await q.answer("Not Admin!", show_alert=True)
            return
        if not admin_auth.get(uid):
            context.user_data['awaiting_pass'] = True
            await q.edit_message_text("🔐 Admin Login\n\nপাসওয়ার্ড লিখো:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data='menu')]]))
            return
        total = len(user_data)
        bal = sum([u.get('balance', 0) for u in user_data.values()])
        kb = [
            [InlineKeyboardButton(f"👥 All Users ({total})", callback_data='admin_users')],
            [InlineKeyboardButton("📢 Broadcast", callback_data='admin_broadcast')],
            [InlineKeyboardButton("🚪 Logout", callback_data='admin_logout')],
            [InlineKeyboardButton("🔙 Back", callback_data='menu')],
        ]
        await q.edit_message_text(f"🔐 ADMIN PANEL\n\n👥 Users: {total}\n💰 Total: {bal} Taka\n✅ Logged In", reply_markup=InlineKeyboardMarkup(kb))

    elif data == 'admin_logout':
        admin_auth[uid] = False
        kb = await get_main_menu(uid)
        await q.edit_message_text("🚪 Logged out! Main Menu:", reply_markup=InlineKeyboardMarkup(kb))

    elif data == 'admin_users':
        if uid != ADMIN_ID or not admin_auth.get(uid):
            return
        msg = "👥 **User List:**\n\n"
        for i, (k, v) in enumerate(list(user_data.items())[:20]):
            msg += f"{i+1}. {v.get('name')} - ID:{k} - Bal:{v.get('balance')}৳\n"
        await q.edit_message_text(msg[:4000], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin", callback_data='admin_panel')]]))

    elif data == 'admin_broadcast':
        if uid != ADMIN_ID or not admin_auth.get(uid):
            return
        context.user_data['awaiting_broadcast'] = True
        await q.edit_message_text("📢 Broadcast ON\n\nযে মেসেজ লিখবে সবাই পাবে:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data='admin_panel')]]))

    elif data == 'menu':
        kb = await get_main_menu(uid)
        await q.edit_message_text("Main Menu:", reply_markup=InlineKeyboardMarkup(kb))

    elif data == 'earn':
        if uid in user_data:
            user_data[uid]['balance'] += 2
        kb = await get_main_menu(uid)
        await q.edit_message_text(f"✅ +2 Taka Added!\nBalance: {user_data[uid]['balance']}", reply_markup=InlineKeyboardMarkup(kb))

    elif data == 'askai':
        await q.edit_message_text("🤖 AI Mode ON! এখন যা খুশি লেখো...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data='menu')]]))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    txt = update.message.text

    if context.user_data.get('awaiting_pass') and uid == ADMIN_ID:
        if txt.strip() == ADMIN_PASSWORD:
            admin_auth[uid] = True
            context.user_data['awaiting_pass'] = False
            total = len(user_data)
            kb = [
                [InlineKeyboardButton(f"👥 All Users ({total})", callback_data='admin_users')],
                [InlineKeyboardButton("📢 Broadcast", callback_data='admin_broadcast')],
                [InlineKeyboardButton("🚪 Logout", callback_data='admin_logout')],
            ]
            await update.message.reply_text(f"✅ Password Correct!\n\n🔐 ADMIN PANEL\n👥 Users: {total}", reply_markup=InlineKeyboardMarkup(kb))
        else:
            await update.message.reply_text("❌ Wrong Password!")
        return

    if context.user_data.get('awaiting_broadcast') and uid == ADMIN_ID and admin_auth.get(uid):
        context.user_data['awaiting_broadcast'] = False
        sent = 0
        for k in user_data.keys():
            try:
                await context.bot.send_message(chat_id=k, text=f"📢 Admin:\n\n{txt}")
                sent += 1
            except:
                pass
        await update.message.reply_text(f"✅ Sent to {sent} users")
        return

    if txt.startswith('/'):
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = ask_gemini(txt)
    await update.message.reply_text(reply[:4000])

async def error_handler(update, context):
    logging.error(f"Error: {context.error}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    print("Bot Starting... Admin Fixed, Menu Fixed")
    app.run_polling()

if __name__ == '__main__':
    main()