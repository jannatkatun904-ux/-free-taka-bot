import os, logging, requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_TOKEN = os.getenv("GEMINI_TOKEN")
ADMIN_ID = 8003993365
ADMIN_PASSWORD = "Raihan01@#@"

user_data = {}
admin_auth = {}
logging.basicConfig(level=logging.INFO)

def ask_gemini(p):
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        h = {"Content-Type": "application/json", "X-goog-api-key": GEMINI_TOKEN}
        d = {"contents": [{"parts": [{"text": p}]}]}
        r = requests.post(url, headers=h, json=d, timeout=20)
        j = r.json()
        if 'candidates' not in j:
            return "❌ Gemini Token Expire! aistudio.google.com থেকে নতুন AIza... Key নিয়ে GEMINI_TOKEN এ বসাও"
        return j['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Error: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_data: user_data[uid] = {'balance':0, 'name':update.effective_user.first_name}
    kb = [[InlineKeyboardButton("💰 Earn", callback_data='earn')], [InlineKeyboardButton("🤖 Ask AI", callback_data='askai')]]
    if uid == ADMIN_ID: kb.append([InlineKeyboardButton("🔐 Admin Panel", callback_data='admin_panel')])
    await update.message.reply_text("Bot Ready! ✅", reply_markup=InlineKeyboardMarkup(kb))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    d = q.data
    if d == 'admin_panel':
        if uid != ADMIN_ID: return
        if not admin_auth.get(uid):
            context.user_data['awaiting_pass'] = True
            await q.edit_message_text("🔐 Admin Login\n\nপাসওয়ার্ড লিখো:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data='menu')]]))
            return
        kb = [[InlineKeyboardButton(f"👥 All Users ({len(user_data)})", callback_data='admin_users')], [InlineKeyboardButton("📢 Broadcast", callback_data='admin_broadcast')], [InlineKeyboardButton("🚪 Logout", callback_data='admin_logout')]]
        await q.edit_message_text(f"🔐 ADMIN PANEL\n👥 Users: {len(user_data)}\n✅ Logged In", reply_markup=InlineKeyboardMarkup(kb))
    elif d == 'admin_logout':
        admin_auth[uid]=False
        await q.edit_message_text("Logged out!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data='menu')]]))
    elif d == 'admin_users':
        msg = "👥 Users:\n\n"
        for i,(k,v) in enumerate(list(user_data.items())[:20]): msg+=f"{i+1}. {v.get('name')} - {k} - {v.get('balance')}৳\n"
        await q.edit_message_text(msg[:4000], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data='admin_panel')]]))
    elif d == 'admin_broadcast':
        context.user_data['awaiting_broadcast']=True
        await q.edit_message_text("📢 Broadcast - মেসেজ লিখো:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data='admin_panel')]]))
    elif d == 'menu': await start(update, context)
    elif d == 'earn':
        user_data[uid]['balance']+=2
        await q.edit_message_text(f"✅ +2 Taka", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data='menu')]]))
    elif d == 'askai':
        await q.edit_message_text("🤖 AI ON!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data='menu')]]))

async def handle_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    txt = update.message.text
    if context.user_data.get('awaiting_pass') and uid == ADMIN_ID:
        if txt.strip() == ADMIN_PASSWORD:
            admin_auth[uid]=True
            context.user_data['awaiting_pass']=False
            kb = [[InlineKeyboardButton(f"👥 All Users ({len(user_data)})", callback_data='admin_users')], [InlineKeyboardButton("📢 Broadcast", callback_data='admin_broadcast')], [InlineKeyboardButton("🚪 Logout", callback_data='admin_logout')]]
            await update.message.reply_text(f"✅ Password Correct!\n\n🔐 ADMIN PANEL\n👥 Users: {len(user_data)}", reply_markup=InlineKeyboardMarkup(kb))
        else:
            await update.message.reply_text("❌ Wrong Password!")
        return
    if context.user_data.get('awaiting_broadcast') and uid == ADMIN_ID:
        context.user_data['awaiting_broadcast']=False
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