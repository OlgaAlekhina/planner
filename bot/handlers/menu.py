from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from utils.keyboards import get_main_menu_keyboard
import logging

from api_client import api_client

from .events import add_event_start

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Обработчик команды /start - показывает главное меню """
    telegram_id = update.effective_user.id

    # Проверяем, авторизован ли пользователь
    result = api_client.check_telegram_user(telegram_id)

    if result.get('exists'):
        user = result['user']
        await update.message.reply_text(f"✅ Добро пожаловать,  {user['first_name'] or user['nickname']}!\n\n")
    else:
        await update.message.reply_text(
            "👋 Добро пожаловать в бота приложения Family Planner!\n\n"
            "Используйте команду /auth, чтобы авторизоваться и получить полный доступ к функционалу бота."
        )

    text = (
        #f"👋 {welcome_text}\n\n"
        f"📱 Что вы хотите сделать?\n\n"
        f"• 📰 Новости - последние обновления\n"
        f"• 🆘 Поддержка - помощь и обратная связь\n"
        f"• ⚡ Быстрое добавление события в свой календарь"
    )

    await update.message.reply_text(text, reply_markup=get_main_menu_keyboard())


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Обработка нажатий на кнопки главного меню """
    query = update.callback_query
    await query.answer()

    section = query.data.replace("section_", "")

    # if section == "news":
    #     from handlers.news import show_news
    #     await show_news(update, context)
    # elif section == "support":
    #     from handlers.support import support_start
    #     await support_start(update, context)
    if section == "quick_event":
        await add_event_start(update, context)
    elif section == "main":
        await show_main_menu(update, context)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Показывает главное меню (вызывается из других разделов) """
    query = update.callback_query

    text = "📱 Главное меню\n\nВыберите раздел:"

    await query.edit_message_text(text, reply_markup=get_main_menu_keyboard())


def get_menu_handlers():
    """ Возвращает обработчики меню """
    return [
        CommandHandler('start', start),
        CommandHandler('menu', start),  # /menu тоже показывает меню
        CallbackQueryHandler(menu_callback, pattern="^section_"),
        CallbackQueryHandler(show_main_menu, pattern="^menu_main$")
    ]