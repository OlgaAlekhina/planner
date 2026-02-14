import os
import sys

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters

# Добавляем путь к корневой папке бота для импортов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import api_client  # импорт из той же папки, что и main.py

import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Состояния диалога
EMAIL, CODE = range(2)

async def start_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Начало процесса авторизации """
    telegram_id = update.effective_user.id
    logger.info(f"🟡 start_auth вызван, telegram_id: {telegram_id}")

    # Проверяем, может пользователь уже авторизован
    result = api_client.check_telegram_user(telegram_id)
    logger.info(f"🟡 Результат check_telegram_user: {result}")

    if result.get('exists'):
        user = result['user']
        logger.info(f"🟢 Пользователь найден: {user['email']}")
        await update.message.reply_text(
            f"✅ Вы уже авторизованы\n"
            #f"Используйте /menu"
        )
        return ConversationHandler.END
    else:
        logger.info("🔴 Пользователь не найден, запрашиваем email")
        await update.message.reply_text(
            "🔐 Вход\n\n"
            "Введите email, под которым вы регистрировались в приложении:"
        )
        return EMAIL

async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Получение email от пользователя """
    email = update.message.text.strip().lower()
    context.user_data['email'] = email
    logger.info(f"📧 Получен email: {email}")

    # Проверяем, что пользователь с таким email существует в БД и отправляем ему код в письме
    result = api_client.check_email(email)

    if 'error' in result:
        await update.message.reply_text("❌ Ошибка связи. Пожалуйста, попробуйте позже.")
        return ConversationHandler.END

    await update.message.reply_text(
        f"📧 На ваш почтовый адрес: {email} был отправлен код подтверждения.\n\n"
        "Введите его для завершения авторизации:"
    )
    return CODE

async def receive_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Получение кода и аутентификация через API """
    code = update.message.text
    email = context.user_data['email']
    telegram_id = update.effective_user.id

    logger.info(f"🔐 Попытка аутентификации: email={email}, telegram_id={telegram_id}, code={code}")

    # Авторизуем через API
    logger.info("🟡 Отправляем запрос к API...")
    result = api_client.authenticate_user(email, int(code), telegram_id)

    logger.info(f"📋 Результат аутентификации: {result}")

    if result.get('success'):
        user = result['user']
        await update.message.reply_text(
            f"🎉 Вы успешно авторизовались!\n\n"
            f"Добро пожаловать, {user['first_name'] or user['nickname']}!\n"
            f"Теперь вам доступен весь функционал бота.\n\n"
        )
    else:
        error_message = result.get('message', 'Неизвестная ошибка')
        logger.error(f"❌ Ошибка авторизации: {error_message}")
        await update.message.reply_text(
            f"❌ Ошибка авторизации: {error_message}\n\n"
            f"Пожалуйста, попробуйте еще раз: /auth"
        )

    return ConversationHandler.END

async def cancel_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Отмена авторизации """
    await update.message.reply_text(
        "Отмена авторизации\n"
        #"Use /start to begin."
    )
    return ConversationHandler.END

def get_auth_handler():
    """ Возвращает обработчик авторизации """
    return ConversationHandler(
        entry_points=[CommandHandler('auth', start_auth)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email)],
            CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_code)],
        },
        fallbacks=[CommandHandler('cancel', cancel_auth)]
    )