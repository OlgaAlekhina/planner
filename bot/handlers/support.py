from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, CallbackQueryHandler, \
    filters
from utils.keyboards import get_back_button, get_yes_no_keyboard
import logging
from config import ADMIN_CHAT_ID

logger = logging.getLogger(__name__)

# Состояния диалога
WAITING_FOR_MESSAGE = 0


async def support_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало раздела поддержки"""
    query = update.callback_query

    text = (
        "🆘 **Центр поддержки**\n\n"
        "Здесь вы можете:\n"
        "• Задать вопрос\n"
        "• Сообщить о проблеме\n"
        "• Оставить предложение\n\n"
        "Мы ответим вам в ближайшее время."
    )

    keyboard = [
        [InlineKeyboardButton("✉️ Написать сообщение", callback_data="support_new")],
        [InlineKeyboardButton("📋 Мои обращения", callback_data="support_history")],
        get_back_button()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return ConversationHandler.END


async def support_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало нового обращения"""
    query = update.callback_query
    await query.answer()

    # Проверяем авторизацию
    user = update.effective_user
    api_client = context.bot_data.get('api_client')
    result = api_client.check_telegram_user(user.id)

    if not result.get('exists'):
        await query.edit_message_text(
            "❌ Для обращений в поддержку нужно авторизоваться.\n\n"
            "Используйте /auth для входа.",
            reply_markup=InlineKeyboardMarkup([get_back_button()])
        )
        return ConversationHandler.END

    await query.edit_message_text(
        "✉️ **Новое обращение**\n\n"
        "Опишите вашу проблему или вопрос подробно.\n"
        "Мы ответим вам в этом чате.\n\n"
        "✏️ Введите сообщение:"
    )
    return WAITING_FOR_MESSAGE


async def receive_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение сообщения от пользователя"""
    user = update.effective_user
    message_text = update.message.text

    # Отправляем в API
    api_client = context.bot_data.get('api_client')
    result = api_client.send_support_message(user.id, message_text)

    if result.get('success'):
        # Отправляем подтверждение пользователю
        await update.message.reply_text(
            f"✅ Ваше обращение #{result.get('ticket_id', 'новое')} принято!\n\n"
            f"Мы ответим вам в ближайшее время.",
            reply_markup=InlineKeyboardMarkup([get_back_button()])
        )

        # Уведомляем админа (опционально)
        await notify_admin(context, user, message_text, result.get('ticket_id'))
    else:
        await update.message.reply_text(
            "❌ Ошибка при отправке. Попробуйте позже.",
            reply_markup=InlineKeyboardMarkup([get_back_button()])
        )

    return ConversationHandler.END


async def notify_admin(context, user, message, ticket_id):
    """Уведомление администратора о новом обращении"""
    try:
        admin_text = (
            f"📨 **Новое обращение** #{ticket_id}\n\n"
            f"👤 От: {user.full_name}\n"
            f"🆔 ID: {user.id}\n"
            f"📱 Username: @{user.username if user.username else 'нет'}\n\n"
            f"💬 Сообщение:\n{message}"
        )

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_text,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")


async def support_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает историю обращений"""
    query = update.callback_query
    await query.answer()

    # Здесь должен быть запрос к API для получения истории
    text = (
        "📋 **Ваши обращения**\n\n"
        "• #SUP-42 (Открыто) - 15.03.2026\n"
        "• #SUP-38 (Закрыто) - 10.03.2026\n"
        "• #SUP-35 (Отвечено) - 05.03.2026\n\n"
        "Выберите обращение для просмотра:"
    )

    keyboard = [
        [InlineKeyboardButton("#SUP-42", callback_data="support_view_42")],
        [InlineKeyboardButton("#SUP-38", callback_data="support_view_38")],
        [InlineKeyboardButton("#SUP-35", callback_data="support_view_35")],
        [InlineKeyboardButton("◀️ Назад", callback_data="section_support")],
        get_back_button()
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена действия"""
    await update.message.reply_text(
        "❌ Действие отменено",
        reply_markup=InlineKeyboardMarkup([get_back_button()])
    )
    return ConversationHandler.END


def get_support_handler():
    """Возвращает обработчик раздела поддержки"""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(support_new, pattern="^support_new$")],
        states={
            WAITING_FOR_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_support_message)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CallbackQueryHandler(support_start, pattern="^section_support$")
        ]
    )


def get_support_handlers():
    """Возвращает все обработчики поддержки"""
    return [
        CallbackQueryHandler(support_start, pattern="^section_support$"),
        CallbackQueryHandler(support_history, pattern="^support_history$"),
        get_support_handler(),  # ConversationHandler
    ]