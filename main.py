import os
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

keyboard = ReplyKeyboardMarkup(
    [
        ["📤 Submit Post"],
        ["💰 Change Wallet"],
        ["🌍 Country/Language"],
        ["📜 History"],
    ],
    resize_keyboard=True,
)

users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Welcome to GameBowy Creator Hub\n\nSend your X profile link to register.",
        reply_markup=keyboard,
    )

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    text = update.message.text

    if chat_id not in users:
        users[chat_id] = {}

    if "x.com" in text or "twitter.com" in text:
        users[chat_id]["username"] = text

        await update.message.reply_text(
            "✅ X account saved.\n\nNow send wallet address."
        )
        return

    if text.startswith("0x"):
        users[chat_id]["wallet"] = text

        supabase.table("creators").insert(
            {
                "telegram_id": chat_id,
                "username": users[chat_id].get("username"),
                "wallet": text,
            }
        ).execute()

        await update.message.reply_text(
            "✅ Wallet saved successfully.",
            reply_markup=keyboard,
        )
        return

    if text == "📤 Submit Post":
        await update.message.reply_text(
            "Send your X post link."
        )
        return

    if "status" in text:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"📢 New Creator Submission\n\nUser: {chat_id}\n\n{text}",
        )

        await update.message.reply_text(
            "✅ Post submitted successfully."
        )

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, messages))

app.run_polling()
