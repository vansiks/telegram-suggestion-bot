import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# === НАСТРОЙКИ ===
BOT_TOKEN = "8253495388:AAHIMBBOi4VDIPE-_38vAfwaWAmCRejYK1U"  
GROUP_ID = -1003068970627  

# Логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === Шаг 1: /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие при команде /start."""
    await update.message.reply_text(
        "Приветствуем, дорогой подписчик!\n"
        "Напишите сообщение, которое вы хотите предложить для канала."
    )

# === Шаг 2: Обработка сообщения после /start ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает текстовое сообщение от пользователя."""
    user_message = update.message.text
    username = update.message.from_user.username or "нет username"
    full_name = f"{update.message.from_user.first_name} {update.message.from_user.last_name}" if update.message.from_user.last_name else update.message.from_user.first_name

    # Формируем сообщение для группы
    forwarded_message = (
        f"📬 <b>Предложенный пост:</b>\n\n"
        f"{user_message}\n\n"
        f"👤 <b>Отправитель:</b>\n"
        f"• Username: {username}\n"
        f"• Имя: {full_name}\n"
        f"• ID: <code>{update.message.from_user.id}</code>"
    )

    try:
        # Отправляем в группу модераторов
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=forwarded_message,
            parse_mode='HTML'
        )
        # Сообщаем пользователю
        await update.message.reply_text("Сообщение отправлено.")
        logger.info(f"Сообщение от {username} отправлено в группу.")
    except Exception as e:
        logger.error(f"Ошибка при отправке: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

# === Основная функция запуска ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Запуск
    logger.info("Бот запущен...")
    app.run_polling()