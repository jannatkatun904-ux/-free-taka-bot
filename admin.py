# admin.py - আলাদা এডমিন ফাইল
ADMIN_ID = 8003993365
ADMIN_PASSWORD = "Raihan01@#@"

# কে লগইন করেছে মনে রাখবে
admin_authenticated = {}

def is_admin(user_id):
    return user_id == ADMIN_ID

def check_password(user_id, password):
    return password == ADMIN_PASSWORD

def is_logged_in(user_id):
    return admin_authenticated.get(user_id, False)

def login(user_id):
    admin_authenticated[user_id] = True

def logout(user_id):
    admin_authenticated[user_id] = False

def get_admin_keyboard(total_users):
    from telegram import InlineKeyboardButton
    return [
        [InlineKeyboardButton(f"👥 All Users ({total_users})", callback_data='admin_users')],
        [InlineKeyboardButton("📢 Broadcast", callback_data='admin_broadcast')],
        [InlineKeyboardButton("📊 Stats", callback_data='admin_stats')],
        [InlineKeyboardButton("🚪 Logout", callback_data='admin_logout')],
        [InlineKeyboardButton("🔙 Back", callback_data='menu')],
    ]