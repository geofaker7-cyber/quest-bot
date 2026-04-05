from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import time
import os

TOKEN = os.getenv("TOKEN")  # токен бота из Variables Railway

location_history = []  # список (timestamp, lat, lon)
subscribers = set()

DELAY = 30  # задержка 30 в секундах
BROADCAST_INTERVAL = 25  # интервал рассылки 75 секунд

# команда /start для участников
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscribers.add(update.effective_chat.id)
    await update.message.reply_text("Привет! Единорог Амур из города Рума ждет, чтобы вы его нашли. Но как и все с мифическими существами - это будет не просто: раз в минуту сюда будет приходить ссылка на место, где некоторое время назад находился наш Амур")

last_sent_time = 0  # глобально

async def broadcast(context):
    global last_sent_time

    now = time.time()
    target_time = now - DELAY

    chosen_location = None
    chosen_time = None

    # ищем точку:
    # 1. старше 3 минут
    # 2. НОВЕЕ, чем уже отправленная
    for t, lat, lon in location_history:
        if last_sent_time < t <= target_time:
            chosen_location = (lat, lon)
            chosen_time = t

    if chosen_location:
        lat, lon = chosen_location
        last_sent_time = chosen_time

        link = f"https://yandex.ru/maps/?ll={lon}%2C{lat}&z=17&pt={lon},{lat},pm2rdm"

        for chat_id in subscribers:
            try:
                await context.bot.send_message(
                    chat_id,
                         f"📍 Место где недавно проскакал Амур:\n{link}"                )
            except:
                pass



target_ids = {797183969, 987654321}  # Telegram ID Целей

async def handle_location(update, context):
    if update.effective_chat.id not in target_ids:
        return  # игнорируем координаты остальных
    loc = update.message.location
    now = time.time()
    location_history.append((now, loc.latitude, loc.longitude))
    await update.message.reply_text("Локация получена! Теперь она распространяется среди участников игры")



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
