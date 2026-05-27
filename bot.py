import json
import os
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

TOKEN = "8953621345:AAFk8t3SgZZjV83ohkJ5MzRSQHj4RMk8_4k"
ADMIN_ID = 8268062931

REGISTER_X, REGISTER_WALLET, SUBMIT_POST = range(3)

DATA_FILE = "data.json"


# ---------------- SAVE & LOAD ---------------- #

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------- START ---------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "🎮 Welcome BK Creators\n\n"
        "This is where your Game Bowy creator posts are tracked.\n\n"
        "Please register your X account and wallet address."
    )

    keyboard = [
        ["Register X Account"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )


# ---------------- REGISTER X ---------------- #

async def register_x(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Send your X username.\n\nExample: @gamebowy"
    )

    return REGISTER_X


async def save_x(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["x_account"] = update.message.text

    await update.message.reply_text(
        "Now send your wallet address."
    )

    return REGISTER_WALLET


# ---------------- SAVE WALLET ---------------- #

async def save_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):

    wallet = update.message.text
    x_account = context.user_data["x_account"]

    user_id = str(update.effective_user.id)

    data = load_data()

    data[user_id] = {
        "x_account": x_account,
        "wallet": wallet,
        "history": []
    }

    save_data(data)

    keyboard = [
        ["Submit Post"],
        ["Change Wallet Address"],
        ["Country/Language"],
        ["History"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "✅ Registration successful!",
        reply_markup=reply_markup
    )

    return ConversationHandler.END


# ---------------- SUBMIT POST ---------------- #

async def submit_post(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Send your X post link."
    )

    return SUBMIT_POST


async def save_post(update: Update, context: ContextTypes.DEFAULT_TYPE):

    post_link = update.message.text

    user_id = str(update.effective_user.id)

    data = load_data()

    if user_id not in data:
        await update.message.reply_text(
            "Please register first."
        )
        return ConversationHandler.END

    data[user_id]["history"].append(post_link)

    save_data(data)

    x_account = data[user_id]["x_account"]
    wallet = data[user_id]["wallet"]

    # SEND TO YOUR DM
    admin_message = (
        f"📥 NEW CREATOR POST\n\n"
        f"👤 X Account: {x_account}\n"
        f"💰 Wallet: {wallet}\n"
        f"🔗 Post: {post_link}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_message
    )

    await update.message.reply_text(
        "✅ Post submitted successfully."
    )

    return ConversationHandler.END


# ---------------- HISTORY ---------------- #

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)

    data = load_data()

    if user_id not in data:
        await update.message.reply_text(
            "No history found."
        )
        return

    history_list = data[user_id]["history"]

    if not history_list:
        await update.message.reply_text(
            "No submitted posts yet."
        )
        return

    text = "📜 Submission History:\n\n"

    for item in history_list:
        text += f"• {item}\n"

    await update.message.reply_text(text)


# ---------------- CHANGE WALLET ---------------- #

async def change_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Send your new wallet address."
    )

    return REGISTER_WALLET


# ---------------- MAIN ---------------- #

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    register_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^Register X Account$"),
                register_x
            )
        ],
        states={
            REGISTER_X: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    save_x
                )
            ],
            REGISTER_WALLET: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    save_wallet
                )
            ],
        },
        fallbacks=[],
    )

    submit_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^Submit Post$"),
                submit_post
            )
        ],
        states={
            SUBMIT_POST: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    save_post
                )
            ]
        },
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(register_handler)
    app.add_handler(submit_handler)

    app.add_handler(
        MessageHandler(
            filters.Regex("^History$"),
            history
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()
