
import asyncio
import time
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

TOKEN = os.getenv("TOKEN")

location_history = []  # (timestamp, lat, lon)
subscribers = set()

DELAY = 180  # 3 минуты

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscribers.add(update.effective_chat.id)
    await update.message.reply_text("Ты подписан на отслеживание!")

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    now = time.time()

    location_history.append((now, loc.latitude, loc.longitude))
    await update.message.reply_text("Локация получена!")

async def broadcast(context: ContextTypes.DEFAULT_TYPE):
    now = time.time()
    target_time = now - DELAY

    chosen_location = None

    for t, lat, lon in reversed(location_history):
        if t <= target_time:
            chosen_location = (lat, lon)
            break

    if chosen_location:
        lat, lon = chosen_location
        link = f"https://maps.google.com/?q={lat},{lon}"

        for chat_id in subscribers:
            try:
                await context.bot.send_message(
                    chat_id,
                    f"📍 Локация (с задержкой 3 мин):\n{link}"
                )
            except:
                pass

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))

    app.job_queue.run_repeating(broadcast, interval=300, first=10)

    print("Бот запущен")
    await app.run_polling()
    
if __name__ == "__main__":
    # asyncio.run(main())  # старый вариант
    import asyncio
    asyncio.get_event_loop().run_until_complete(main())
