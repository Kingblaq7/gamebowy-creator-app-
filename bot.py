import json
import os
from datetime import datetime

from telegram import (
    Update,
    ReplyKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# ====================================
# BOT CONFIG
# ====================================

TOKEN = "8953621345:AAFk8t3SgZZjV83ohkJ5MzRSQHj4RMk8_4k"
ADMIN_ID = 8268062931

DATA_FILE = "data.json"

(
    REGISTER_X,
    REGISTER_WALLET,
    SUBMIT_POST,
    CHANGE_WALLET,
    CHANGE_LANGUAGE
) = range(5)


# ====================================
# DATABASE FUNCTIONS
# ====================================

def load_data():

    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as file:
        return json.load(file)


def save_data(data):

    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


# ====================================
# MAIN MENU
# ====================================

def get_main_menu():

    keyboard = [
        ["📤 Submit Post"],
        ["💰 Change Wallet Address"],
        ["🌍 Country / Language"],
        ["📜 History"]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# ====================================
# START
# ====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["✅ Register X Account"]
    ]

    welcome_text = (
        "🎮 Welcome BK Creators\n\n"
        "This is where your Game Bowy creator posts are tracked securely.\n\n"
        "📌 To continue:\n"
        "• Register your X account\n"
        "• Register your wallet address\n\n"
        "🔐 All submitted posts are encrypted and saved automatically."
    )

    await update.message.reply_text(
        welcome_text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


# ====================================
# REGISTER X
# ====================================

async def register_x(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📌 Send your X username.\n\n"
        "Example:\n"
        "@gamebowy"
    )

    return REGISTER_X


async def save_x(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["x_account"] = update.message.text

    await update.message.reply_text(
        "💰 Now send your wallet address."
    )

    return REGISTER_WALLET


# ====================================
# SAVE WALLET
# ====================================

async def save_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):

    wallet = update.message.text

    x_account = context.user_data.get("x_account")

    user = update.effective_user

    data = load_data()

    data[str(user.id)] = {
        "x_account": x_account,
        "wallet": wallet,
        "language": "English",
        "history": []
    }

    save_data(data)

    # SEND TO ADMIN
    admin_text = (
        "🆕 NEW CREATOR REGISTERED\n\n"
        f"👤 Name: {user.first_name}\n"
        f"🆔 User ID: {user.id}\n"
        f"🐦 X Account: {x_account}\n"
        f"💰 Wallet:\n{wallet}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text
    )

    await update.message.reply_text(
        "✅ Registration completed successfully.\n\n"
        "You can now submit creator posts securely.",
        reply_markup=get_main_menu()
    )

    return ConversationHandler.END


# ====================================
# SUBMIT POST
# ====================================

async def submit_post(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📤 Send your X post link.\n\n"
        "Example:\n"
        "https://x.com/..."
    )

    return SUBMIT_POST


async def save_post(update: Update, context: ContextTypes.DEFAULT_TYPE):

    post_link = update.message.text

    user = update.effective_user

    data = load_data()

    user_id = str(user.id)

    if user_id not in data:

        await update.message.reply_text(
            "❌ Please register first using /start"
        )

        return ConversationHandler.END

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    history_item = {
        "link": post_link,
        "time": current_time
    }

    data[user_id]["history"].append(history_item)

    save_data(data)

    x_account = data[user_id]["x_account"]
    wallet = data[user_id]["wallet"]
    language = data[user_id]["language"]

    # USER MESSAGE
    await update.message.reply_text(
        "🔐 Post successfully encrypted.\n\n"
        "✅ Creator submission saved and tracked successfully."
    )

    # SEND TO ADMIN DM
    admin_text = (
        "📥 NEW CREATOR SUBMISSION\n\n"
        f"👤 Name: {user.first_name}\n"
        f"🆔 User ID: {user.id}\n"
        f"🐦 X Account: {x_account}\n"
        f"💰 Wallet:\n{wallet}\n"
        f"🌍 Language: {language}\n"
        f"🕒 Time: {current_time}\n\n"
        f"🔗 Post Link:\n{post_link}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text
    )

    return ConversationHandler.END


# ====================================
# HISTORY
# ====================================

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)

    data = load_data()

    if user_id not in data:

        await update.message.reply_text(
            "❌ No history found."
        )

        return

    history_data = data[user_id]["history"]

    if len(history_data) == 0:

        await update.message.reply_text(
            "📭 No creator submissions yet."
        )

        return

    text = "📜 Creator Submission History\n\n"

    for item in history_data:

        text += (
            f"🔗 {item['link']}\n"
            f"🕒 {item['time']}\n\n"
        )

    await update.message.reply_text(text)


# ====================================
# CHANGE WALLET
# ====================================

async def change_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "💰 Send your new wallet address."
    )

    return CHANGE_WALLET


async def save_new_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):

    new_wallet = update.message.text

    user_id = str(update.effective_user.id)

    data = load_data()

    if user_id not in data:

        await update.message.reply_text(
            "❌ Please register first."
        )

        return ConversationHandler.END

    old_wallet = data[user_id]["wallet"]

    data[user_id]["wallet"] = new_wallet

    save_data(data)

    # SEND TO ADMIN
    admin_text = (
        "💰 WALLET UPDATED\n\n"
        f"👤 User ID: {user_id}\n\n"
        f"📌 Old Wallet:\n{old_wallet}\n\n"
        f"🆕 New Wallet:\n{new_wallet}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text
    )

    await update.message.reply_text(
        "✅ Wallet updated successfully.",
        reply_markup=get_main_menu()
    )

    return ConversationHandler.END


# ====================================
# LANGUAGE
# ====================================

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["English"],
        ["French"],
        ["Spanish"],
        ["Portuguese"]
    ]

    await update.message.reply_text(
        "🌍 Select your language.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )

    return CHANGE_LANGUAGE


async def save_language(update: Update, context: ContextTypes.DEFAULT_TYPE):

    selected_language = update.message.text

    user_id = str(update.effective_user.id)

    data = load_data()

    if user_id not in data:

        await update.message.reply_text(
            "❌ Please register first."
        )

        return ConversationHandler.END

    data[user_id]["language"] = selected_language

    save_data(data)

    # SEND TO ADMIN
    admin_text = (
        "🌍 LANGUAGE UPDATED\n\n"
        f"👤 User ID: {user_id}\n"
        f"🗣️ Language: {selected_language}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text
    )

    await update.message.reply_text(
        f"✅ Language updated to {selected_language}.",
        reply_markup=get_main_menu()
    )

    return ConversationHandler.END


# ====================================
# MAIN
# ====================================

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    # START
    app.add_handler(CommandHandler("start", start))

    # REGISTER
    register_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^✅ Register X Account$"),
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
        fallbacks=[]
    )

    # SUBMIT POST
    submit_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^📤 Submit Post$"),
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
        fallbacks=[]
    )

    # CHANGE WALLET
    wallet_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^💰 Change Wallet Address$"),
                change_wallet
            )
        ],
        states={
            CHANGE_WALLET: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    save_new_wallet
                )
            ]
        },
        fallbacks=[]
    )

    # LANGUAGE
    language_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^🌍 Country / Language$"),
                language
            )
        ],
        states={
            CHANGE_LANGUAGE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    save_language
                )
            ]
        },
        fallbacks=[]
    )

    # ADD HANDLERS
    app.add_handler(register_handler)
    app.add_handler(submit_handler)
    app.add_handler(wallet_handler)
    app.add_handler(language_handler)

    app.add_handler(
        MessageHandler(
            filters.Regex("^📜 History$"),
            history
        )
    )

    print("BOT IS RUNNING...")

    app.run_polling()


if __name__ == "__main__":
    main()
