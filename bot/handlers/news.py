from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from utils.keyboards import get_back_button
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def show_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список новостей"""
    query = update.callback_query

    # Получаем новости из API
    api_client = context.bot_data.get('api_client')
    news_data = api_client.get_news(limit=5)

    if news_data.get('error'):
        text = "❌ Не удалось загрузить новости. Попробуйте позже."
        keyboard = [get_back_button()]
    elif not news_data.get('results'):
        text = "📰 Новостей пока нет.\n\nЗагляните позже!"
        keyboard = [get_back_button()]
    else:
        text = "📰 **Последние новости**\n\n"

        # Формируем список новостей
        for i, news in enumerate(news_data['results'][:5], 1):
            date = datetime.fromisoformat(news['created_at']).strftime('%d.%m.%Y')
            text += f"{i}. **{news['title']}**\n"
            text += f"   {date}\n"
            text += f"   {news['preview']}\n\n"

        # Добавляем кнопки для каждой новости
        keyboard = []
        for i, news in enumerate(news_data['results'][:5], 1):
            keyboard.append([
                InlineKeyboardButton(f"📖 Читать новость #{i}", callback_data=f"news_read_{news['id']}")
            ])

    keyboard.append(get_back_button())
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def read_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает полный текст новости"""
    query = update.callback_query
    await query.answer()

    news_id = query.data.replace("news_read_", "")

    # Здесь должен быть запрос к API для получения полной новости
    # Пока используем заглушку
    text = (
        f"📰 **Заголовок новости**\n\n"
        f"📅 15.03.2026\n\n"
        f"Полный текст новости здесь...\n\n"
        f"Это пример содержимого новости. "
        f"В реальном приложении здесь будет текст из базы данных."
    )

    keyboard = [
        [InlineKeyboardButton("◀️ К списку новостей", callback_data="section_news")],
        get_back_button()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


def get_news_handlers():
    """Возвращает обработчики раздела новостей"""
    return [
        CallbackQueryHandler(show_news, pattern="^section_news$"),
        CallbackQueryHandler(read_news, pattern="^news_read_")
    ]