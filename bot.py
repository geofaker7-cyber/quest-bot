from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import time
import os

TOKEN = os.getenv("TOKEN")  # токен бота из Variables Railway

location_history = []  # список (timestamp, lat, lon)
subscribers = set()

DELAY = 60  # задержка 3 минуты в секундах
BROADCAST_INTERVAL = 180  # интервал рассылки 5 минут

# команда /start для участников
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscribers.add(update.effective_chat.id)
    await update.message.reply_text("Ты подписан на отслеживание!")

# обработка геолокации от цели
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    now = time.time()
    location_history.append((now, loc.latitude, loc.longitude))
    await update.message.reply_text("Локация получена!")

# функция рассылки каждые 5 минут
async def broadcast(context: ContextTypes.DEFAULT_TYPE):
    now = time.time()
    target_time = now - DELAY  # берём координату с задержкой 3 минуты

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

# основной запуск бота
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # запускаем JobQueue для broadcast
    app.job_queue.run_repeating(broadcast, interval=BROADCAST_INTERVAL, first=10)

    print("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
