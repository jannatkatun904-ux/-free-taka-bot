# admin.py - Admin Panel File
ADMIN_ID = 8003993365  # তোমার ID

ADMIN_MENU_TEXT = """
🔐 **ADMIN PANEL**

👥 Total Users: {total_users}
💰 Total Balance: {total_bal} Taka
🆔 Admin ID: {admin_id}

Select Option:
"""

def is_admin(user_id):
    return user_id == ADMIN_ID

def get_admin_keyboard(total_users):
    from telegram import InlineKeyboardButton
    return [
        [InlineKeyboardButton(f"👥 All Users ({total_users})", callback_data='admin_users')],
        [InlineKeyboardButton("📢 Broadcast Message", callback_data='admin_broadcast')],
        [InlineKeyboardButton("💵 Add Balance to User", callback_data='admin_addbal')],
        [InlineKeyboardButton("📊 Bot Stats", callback_data='admin_stats')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='menu')],
    ]