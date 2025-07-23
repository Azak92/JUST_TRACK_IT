import os
from datetime import date

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)
from dotenv import load_dotenv
from supabase import create_client, Client

# ─── Load Secrets ───────────────────────────────────────────────────────────────
load_dotenv()
BOT_TOKEN       = os.getenv("TELEGRAM_BOT_TOKEN")
SUPABASE_URL    = os.getenv("SUPABASE_URL")
SUPABASE_KEY    = os.getenv("SUPABASE_SERVICE_KEY")

# ─── Initialize Supabase Client ────────────────────────────────────────────────
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─── Map Telegram IDs → Supabase user_id ───────────────────────────────────────
# (Later you can store this mapping in your DB rather than hard-coding.)
telegram_user_map = {
    248294672: "f10c86ee-e53e-409e-a406-c2f25b96ea3a",
    # add more mappings as you onboard users
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is issued."""
    await update.message.reply_text(
        "👋 Welcome to JustTrackIt Bot!\n"
        "Send me your weight (e.g. “81.3”) and I’ll log it for you."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parse the incoming text as a weight, then insert into Supabase."""
    text = update.message.text.strip()
    telegram_id = update.effective_user.id

    # 1️⃣ Try to parse the message as a float
    try:
        weight = float(text)
    except ValueError:
        return await update.message.reply_text(
            "❌ I couldn’t read that as a number. "
            "Please send just your weight like `81.3`."
        )

    # 2️⃣ Find the linked user in Supabase
    user_id = telegram_user_map.get(telegram_id)
    if not user_id:
        return await update.message.reply_text(
            "⚠️ You haven’t been registered yet. "
            "Ask the admin to link your Telegram ID to your account."
        )

    # 3️⃣ Insert into the weights table
    today = date.today().isoformat()
    try:
        response = supabase.table("weight_logs").insert({
            "user_id": user_id,
            "weight": weight,
            "logged_at": today
        }).execute()
         # 📣 Print to console so it “stays” in your logs
        print(f'Weight of {weight} kg is logged successfully at {today}')
    except Exception as e:
        # any network/JSON/RLS/etc. error will be caught here
        return await update.message.reply_text(f"🚨 Failed to log weight:\n{e}")

    # # 4️⃣ Check for errors, not status_code
    # if response.error is None:
    #     await update.message.reply_text(f"✅ Logged **{weight} kg** at {today}!")
    # else:
    #     # you can inspect response.error for details
    #     await update.message.reply_text(
    #         f"🚨 Failed to log weight:\n{response.error}"
    #     )

# Main app
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()