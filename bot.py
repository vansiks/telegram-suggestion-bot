import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

# === НАСТРОЙКИ ===
BOT_TOKEN = "8253495388:AAHIMBBOi4VDIPE-_38vAfwaWAmCRejYK1U"  # Замени на свой
GROUP_ID = -1003068970627  # Замени на ID группы

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Приветствуем, дорогой подписчик!\n"
        "Напишите сообщение, которое вы хотите предложить для канала."
    )

# === Обработка всех типов контента от пользователя ===
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    # Собираем информацию о пользователе
    username = f"@{user.username}" if user.username else "нет username"
    full_name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name

    # Подпись в группу
    caption = (
        f"📬 <b>Предложенный контент:</b>\n\n"
        f"👤 <b>Отправитель:</b>\n"
        f"• Username: {username}\n"
        f"• Имя: {full_name}\n"
    )

    try:
        # === ТЕКСТ ===
        if message.text:
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=caption + f"\n📝 <b>Текст:</b>\n{message.text}",
                parse_mode='HTML'
            )
            await message.reply_text("Сообщение отправлено.")

        # === ФОТО ===
        elif message.photo:
            file_id = message.photo[-1].file_id  # Самое качественное фото
            caption_msg = caption + f"\n🖼 <b>Фото</b>"
            await context.bot.send_photo(
                chat_id=GROUP_ID,
                photo=file_id,
                caption=caption_msg,
                parse_mode='HTML'
            )
            await message.reply_text("Сообщение отправлено.")

        # === ВИДЕО ===
        elif message.video:
            file_id = message.video.file_id
            caption_msg = (
                caption +
                f"\n🎥 <b>Видео</b>\n"
                f"Размер: {message.video.file_size // 1024} КБ"
            )
            await context.bot.send_video(
                chat_id=GROUP_ID,
                video=file_id,
                caption=caption_msg,
                parse_mode='HTML'
            )
            await message.reply_text("Сообщение отправлено.")

        # === GIF (анимация) ===
        elif message.animation:
            file_id = message.animation.file_id
            caption_msg = (
                caption +
                f"\n🎬 <b>GIF / Анимация</b>\n"
                f"Размер: {message.animation.file_size // 1024} КБ"
            )
            await context.bot.send_animation(
                chat_id=GROUP_ID,
                animation=file_id,
                caption=caption_msg,
                parse_mode='HTML'
            )
            await message.reply_text("Сообщение отправлено.")

        # === АУДИО (музыка) ===
        elif message.audio:
            file_id = message.audio.file_id
            title = message.audio.title or "Без названия"
            caption_msg = (
                caption +
                f"\n🎵 <b>Аудио</b>\n"
                f"Название: {title}"
            )
            await context.bot.send_audio(
                chat_id=GROUP_ID,
                audio=file_id,
                caption=caption_msg,
                parse_mode='HTML'
            )
            await message.reply_text("Сообщение отправлено.")

        # === ГОЛОСОВОЕ СООБЩЕНИЕ ===
        elif message.voice:
            file_id = message.voice.file_id
            duration = message.voice.duration
            caption_msg = (
                caption +
                f"\n🗣 <b>Голосовое</b>\n"
                f"Длительность: {duration} сек."
            )
            await context.bot.send_voice(
                chat_id=GROUP_ID,
                voice=file_id,
                caption=caption_msg,
                parse_mode='HTML'
            )
            await message.reply_text("Сообщение отправлено.")


        # === ВИДЕО-СООБЩЕНИЕ (кружок) ===
        elif message.video_note:
            file_id = message.video_note.file_id
            duration = message.video_note.duration
            caption_msg = (
                caption +
                f"\n🔴 <b>Видео-сообщение</b>\n"
                f"Длительность: {duration} сек."
            )
            await context.bot.send_video_note(chat_id=GROUP_ID, video_note=file_id)
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=caption_msg,
                parse_mode='HTML'
            )
            await message.reply_text("Сообщение отправлено.")

        # === СТИКЕР ===
        elif message.sticker:
            file_id = message.sticker.file_id
            emoji = message.sticker.emoji or "❓"
            caption_msg = (
                caption +
                f"\n🔖 <b>Стикер</b>\n"
                f"Эмодзи: {emoji}"
            )
            await context.bot.send_sticker(chat_id=GROUP_ID, sticker=file_id)
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=caption_msg,
                parse_mode='HTML'
            )
            await message.reply_text("Сообщение отправлено.")

        else:
            # Неизвестный тип
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=caption + "\n📩 <b>Неизвестный тип контента</b>",
                parse_mode='HTML'
            )
            await message.reply_text("Сообщение отправлено.")

        logger.info(f"Контент от {username} ({user.id}) отправлен в группу.")
    except Exception as e:
        logger.error(f"Ошибка при отправке: {e}")
        await message.reply_text("❌ Ошибка при отправке. Попробуйте позже.")

# === Обработка ответа модератора в группе ===
async def handle_reply_in_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # Проверяем, что это ответ на сообщение бота
    if not message.reply_to_message or not message.text:
        return

    replied = message.reply_to_message

    # Ищем ID пользователя в тексте сообщения бота
    import re
    match = re.search(r"ID: <code>(\d+)</code>", replied.text)
    if not match:
        return  # Не нашли ID — выходим

    user_id = int(match.group(1))

    # Проверяем, что ответил модератор (не бот и не пользователь)
    if message.from_user.id == context.bot.id:
        return

    try:
        # Отправляем ответ пользователю
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📬 Ответ от модератора:\n\n{message.text}"
        )
        # Подтверждение в группе
        await message.reply_text("✅ Ответ отправлен пользователю.")
        logger.info(f"Ответ отправлен пользователю {user_id}")
    except Exception as e:
        error_msg = str(e).lower()
        if "blocked" in error_msg or "kicked" in error_msg:
            await message.reply_text("❌ Пользователь заблокировал бота.")
        else:
            await message.reply_text(f"❌ Ошибка при отправке: {e}")
        logger.error(f"Ошибка при отправке ответа пользователю {user_id}: {e}")

# === ЗАПУСК ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Обработчики
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.ALL, handle_user_message))  # Все типы контента
    app.add_handler(MessageHandler(filters.REPLY, handle_reply_in_group))  # Ответы в группе

    logger.info("✅ Бот запущен и работает автономно...")
    app.run_polling()