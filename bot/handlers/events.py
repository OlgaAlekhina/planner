import os
import sys
from datetime import datetime, time, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, CallbackQueryHandler, \
    filters

# Добавляем путь к корневой папке бота для импортов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import api_client
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

import logging

logger = logging.getLogger(__name__)

# Состояния диалога
TITLE, DATE, TIME, CONFIRM = range(4)


# Вспомогательная функция для создания кнопок выбора времени
def create_time_keyboard():
    """Создает клавиатуру с выбором времени (часы с интервалом 1 час)"""
    keyboard = []
    row = []

    # Создаем кнопки для каждого часа с 00:00 до 23:00
    for hour in range(0, 24):
        time_str = f"{hour:02d}:00"
        row.append(InlineKeyboardButton(time_str, callback_data=f"time_{hour}"))

        # По 4 кнопки в ряд
        if len(row) == 4 or hour == 23:
            keyboard.append(row)
            row = []

    # Добавляем кнопку "Сейчас" для быстрого выбора
    keyboard.append([InlineKeyboardButton("🕐 Текущее время", callback_data="time_now")])

    return InlineKeyboardMarkup(keyboard)


async def add_event_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Начало процесса добавления события """
    # Проверяем, откуда пришел вызов (из callback или из команды)
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        message = query.message
        user = query.from_user
        reply_method = lambda text, **kwargs: query.edit_message_text(text, **kwargs)
    else:
        message = update.message
        user = update.effective_user
        reply_method = lambda text, **kwargs: update.message.reply_text(text, **kwargs)

    query = update.callback_query

    telegram_id = user.id
    logger.info(f"🟡 Начало добавления события, telegram_id: {telegram_id}")

    # Проверяем, авторизован ли пользователь
    result = api_client.check_telegram_user(telegram_id)
    logger.info(f"🟡 Проверка авторизации: {result}")

    if not result.get('exists'):
        logger.info("🔴 Пользователь не авторизован")
        await reply_method(
            "❌ Для добавления событий необходимо авторизоваться.\n\n"
            "Используйте /auth для входа."
        )
        return ConversationHandler.END

    # Сохраняем данные пользователя в контекст
    context.user_data['user'] = result['user']

    await reply_method(
        "📝 Добавление нового события\n\n"
        "Введите название события:"
    )
    logger.info("🟢 Переходим в состояние TITLE")
    return TITLE


async def receive_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Получение названия события """
    logger.info("🟡 Вход в функцию receive_title")
    logger.info(f"🟡 Текущее состояние: {context.user_data.get('_state')}")
    logger.info(f"🟡 Текст сообщения: {update.message.text}")
    title = update.message.text.strip()
    context.user_data['event_title'] = title

    logger.info(f"📝 Получено название: {title}")

    await update.message.reply_text(
        f"✅ Название: {title}\n\n"
        f"Теперь выберите дату события:"
    )

    # Запускаем календарь для выбора даты
    calendar, step = DetailedTelegramCalendar(calendar_id=1, current_date=datetime.now().date()).build()
    await update.message.reply_text(
        f"Выберите дату:",
        reply_markup=calendar
    )

    return DATE


async def calendar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Обработка выбора даты из календаря """
    query = update.callback_query
    await query.answer()

    result, key, step = DetailedTelegramCalendar(calendar_id=1, current_date=datetime.now().date()).process(query.data)

    if not result and key:
        # Еще выбираем дату (переход по месяцам)
        await query.edit_message_text(
            f"Выберите дату:",
            reply_markup=key
        )
    elif result:
        # Дата выбрана
        context.user_data['event_date'] = result
        logger.info(f"📅 Выбрана дата: {result}")

        await query.edit_message_text(
            f"✅ Выбрана дата: {result.strftime('%d.%m.%Y')}\n\n"
            f"Теперь выберите время:"
        )

        # Показываем клавиатуру с выбором времени
        await query.message.reply_text(
            "Выберите время начала:",
            reply_markup=create_time_keyboard()
        )
        return TIME


async def time_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Обработка выбора времени """
    query = update.callback_query
    await query.answer()

    if query.data == "time_now":
        # Выбрано текущее время
        selected_time = datetime.now().time()
        # Округляем до ближайшего часа
        if selected_time.minute > 30:
            selected_time = time((selected_time.hour + 1) % 24, 0, 0)
        else:
            selected_time = time(selected_time.hour, 0, 0)
    else:
        # Выбран конкретный час
        hour = int(query.data.split('_')[1])
        selected_time = time(hour, 0, 0)

    context.user_data['event_time'] = selected_time

    # Формируем полную дату и время
    event_datetime = datetime.combine(
        context.user_data['event_date'],
        selected_time
    )
    context.user_data['event_datetime'] = event_datetime

    logger.info(f"⏰ Выбрано время: {selected_time.strftime('%H:%M')}")

    # Показываем подтверждение
    title = context.user_data['event_title']

    # Создаем клавиатуру подтверждения
    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data="event_confirm_yes"),
            InlineKeyboardButton("❌ Отмена", callback_data="event_confirm_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"📝 Проверьте данные события:\n\n"
        f"📌 Название: {title}\n"
        f"📅 Дата: {event_datetime.strftime('%d.%m.%Y')}\n"
        f"⏰ Время: {event_datetime.strftime('%H:%M')}\n\n"
        f"Всё верно?",
        reply_markup=reply_markup
    )
    return CONFIRM


async def confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Подтверждение создания события """
    query = update.callback_query
    await query.answer()

    if query.data == "event_confirm_yes":
        # Отправляем данные в API
        event_datetime = context.user_data['event_datetime']

        # Получаем данные пользователя из контекста
        user_data = context.user_data.get('user', {})
        user_id = user_data.get('id')

        # Форматируем дату для API
        event_date = event_datetime.strftime('%Y-%m-%d')
        event_time = event_datetime.strftime('%H:%M')

        # Создаем событие через API
        result = api_client.create_event(
            user_id=user_id,
            title=context.user_data['event_title'],
            date=event_date,
            time=event_time
        )

        logger.info(f"📋 Результат создания события: {result}")

        if result.get('success'):
            await query.edit_message_text(
                f"✅ Событие успешно создано!\n\n"
                f"📌 {context.user_data['event_title']}\n"
                f"📅 {event_datetime.strftime('%d.%m.%Y %H:%M')}\n\n"
                f"Вы можете добавить еще одно: /add_event"
            )
        else:
            error_message = result.get('message', 'Неизвестная ошибка')
            await query.edit_message_text(
                f"❌ Ошибка при создании мероприятия: {error_message}"
            )
    else:
        # Отмена
        await query.edit_message_text(
            "❌ Создание мероприятия отменено.\n\n"
            "Чтобы попробовать снова: /add_event"
        )

    # Очищаем данные пользователя
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Отмена добавления события """
    await update.message.reply_text(
        "❌ Добавление события отменено.\n\n"
        "Чтобы попробовать снова: /add_event"
    )
    return ConversationHandler.END


def get_add_event_handler():
    """ Возвращает обработчик добавления события """
    return ConversationHandler(
        entry_points=[
            CommandHandler('addevent', add_event_start),
            CallbackQueryHandler(add_event_start, pattern="^section_quick_event$")
        ],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_title)],
            DATE: [CallbackQueryHandler(calendar_callback)],
            TIME: [CallbackQueryHandler(time_callback)],
            CONFIRM: [CallbackQueryHandler(confirm_callback, pattern="^event_confirm_")],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CallbackQueryHandler(add_event_start, pattern="^section_quick_event$")
        ],
        name="add_event_conversation",
        persistent=False,
        allow_reentry=True
    )