import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.helpers import escape_markdown

# Çevre değişkenleri (Railway Dashboard > Variables kısmına girilecek)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # örn: @KatreSms

DATA_FILE = "users.json"

def load_users():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

users = load_users()

# 📌 /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    if user_id not in users:
        users[user_id] = {"tokens": 0, "refs": [], "pending_refs": []}
        save_users(users)

    # Menü
    keyboard = [
        [InlineKeyboardButton("🎁 Jetonlarım", callback_data="my_tokens")],
        [InlineKeyboardButton("🎯 Referans Linkim", callback_data="my_ref")],
        [InlineKeyboardButton("📱 Numara Al", callback_data="get_number")]
    ]
    await update.message.reply_text("✅ Hoşgeldin! Menünü buradan yönetebilirsin:", 
        reply_markup=InlineKeyboardMarkup(keyboard))

# 📌 Menü işlemleri
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    if user_id not in users:
        users[user_id] = {"tokens": 0, "refs": [], "pending_refs": []}
        save_users(users)

    if query.data == "my_tokens":
        await query.edit_message_text(f"🎁 Jetonların: {users[user_id]['tokens']}", 
            reply_markup=query.message.reply_markup)

    elif query.data == "my_ref":
        bot_username = (await context.bot.get_me()).username
        ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"
        await query.edit_message_text(
            f"🎯 Referans linkin:\n{escape_markdown(ref_link)}",
            parse_mode="MarkdownV2",
            reply_markup=query.message.reply_markup)

    elif query.data == "get_number":
        tokens = users[user_id]["tokens"]
        if tokens >= 5:
            users[user_id]["tokens"] -= 5
            save_users(users)
            await query.edit_message_text(
                "📱 Numara alma hakkın var!\nAdmin ile iletişime geç → @SiberSubeden",
                reply_markup=query.message.reply_markup)
        else:
            await query.edit_message_text(
                "❌ Yetersiz jeton. En az 5 jeton gerekli.",
                reply_markup=query.message.reply_markup)

# 📌 Admin paneli
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Bu komut sadece admin için.")
    keyboard = [
        [InlineKeyboardButton("👥 Kullanıcı Listesi", callback_data="list_users")],
        [InlineKeyboardButton("➕ Jeton Ekle", callback_data="add_token")],
        [InlineKeyboardButton("➖ Jeton Sil", callback_data="remove_token")],
        [InlineKeyboardButton("📋 Referans Bekleyenler", callback_data="pending_refs")],
        [InlineKeyboardButton("📂 JSON Dışa Aktar", callback_data="export_json")]
    ]
    await update.message.reply_text("⚙️ Admin Paneli:", 
        reply_markup=InlineKeyboardMarkup(keyboard))

# 📌 Botu başlat
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.run_polling()

if __name__ == "__main__":
    main()