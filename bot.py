import os, logging, requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from admin import ADMIN_ID, ADMIN_PASSWORD, is_admin, is_logged_in, login, logout, get_admin_keyboard

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_TOKEN = os.getenv("GEMINI_TOKEN")

user_data = {}
logging.basicConfig(level=logging.INFO)

def ask_gemini(p):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    h = {"Content-Type": "application/json", "X-goog-api-key": GEMINI_TOKEN}
    d = {"contents": [{"parts": [{"text": p}]}]}
    try:
        r = requests.post(url, headers=h, json=d, timeout=20)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"AI Error: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_data: user_data[uid] = {'balance':0, 'name':update.effective_user.first_name}
    kb = [[InlineKeyboardButton("💰 Earn", callback_data='earn')], [InlineKeyboardButton("🤖 Ask AI", callback_data='askai')]]
    if is_admin(uid): kb.append([InlineKeyboardButton("🔐 Admin Panel", callback_data='admin_panel')])
    await update.message.reply_text("Bot Ready! Admin ✅", reply_markup=InlineKeyboardMarkup(kb))

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    if not is_admin(uid): 
        await q.answer("Not Admin!", show_alert=True)
        return
    if not is_logged_in(uid):
        context.user_data['awaiting_admin_pass'] = True
        await q.edit_message_text("🔐 Admin Login\n\nপাসওয়ার্ড লিখো:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data='menu')]]))
        return
    total = len(user_data)
    bal = sum([u.get('balance',0) for u in user_data.values()])
    await q.edit_message_text(f"🔐 ADMIN PANEL\n\n👥 Users: {total}\n💰 Total: {bal} Taka\n✅ Logged In", reply_markup=InlineKeyboardMarkup(get_admin_keyboard(total)))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    d = q.data
    if d == 'admin_panel': await admin_panel(update, context)
    elif d == 'admin_logout':
        logout(uid)
        await q.edit_message_text("🚪 Logged out!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data='menu')]]))
    elif d == 'admin_users':
        if not is_admin(uid) or not is_logged_in(uid): return
        msg = "👥 User List:\n\n"
        for i,(k,v) in enumerate(list(user_data.items())[:20]): msg+=f"{i+1}. {v.get('name')} - ID:{k} - Bal:{v.get('balance')}৳\n"
        await q.edit_message_text(msg[:4000], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data='admin_panel')]]))
    elif d == 'admin_broadcast':
        if not is_admin(uid) or not is_logged_in(uid): return
        context.user_data['awaiting_broadcast'] = True
        await q.edit_message_text("📢 Broadcast ON - মেসেজ লিখো:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data='admin_panel')]]))
    elif d == 'menu': await start(update, context)
    elif d == 'earn':
        if uid in user_data: user_data[uid]['balance']+=2
        await q.edit_message_text(f"✅ +2 Taka", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data='menu')]]))
    elif d == 'askai':
        await q.edit_message_text("🤖 AI ON! লেখো...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data='menu')]]))

async def handle_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    txt = update.message.text
    if context.user_data.get('awaiting_admin_pass') and is_admin(uid):
        if txt.strip() == ADMIN_PASSWORD:
            login(uid)
            context.user_data['awaiting_admin_pass'] = False
            await update.message.reply_text("✅ Password Correct! Raihan01@#@ - আবার Admin Panel ক্লিক করো।")
        else: await update.message.reply_text("❌ Wrong Password!")
        return
    if context.user_data.get('awaiting_broadcast') and is_admin(uid) and is_logged_in(uid):
        context.user_data['awaiting_broadcast'] = False
        sent=0
        for k in user_data.keys():
            try:
                await context.bot.send_message(chat_id=k, text=f"📢 Admin:\n\n{txt}")
                sent+=1
            except: pass
        await update.message.reply_text(f"✅ Sent to {sent} users")
        return
    if txt.startswith('/'): return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text(ask_gemini(txt)[:4000])

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai))
    app.run_polling()

if __name__ == '__main__': main()