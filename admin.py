ADMIN_ID = 8003993365
ADMIN_PASSWORD = "Raihan01@#@"
admin_authenticated = {}

def is_admin(uid): return uid == ADMIN_ID
def is_logged_in(uid): return admin_authenticated.get(uid, False)
def login(uid): admin_authenticated[uid] = True
def logout(uid): admin_authenticated[uid] = False

def get_admin_keyboard(total):
    from telegram import InlineKeyboardButton
    return [
        [InlineKeyboardButton(f"👥 All Users ({total})", callback_data='admin_users')],
        [InlineKeyboardButton("📢 Broadcast", callback_data='admin_broadcast')],
        [InlineKeyboardButton("🚪 Logout", callback_data='admin_logout')],
        [InlineKeyboardButton("🔙 Back", callback_data='menu')],
    ]