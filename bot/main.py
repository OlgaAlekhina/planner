import sys
import time

from telegram import Update
from telegram.error import TimedOut, NetworkError
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes, MessageHandler, filters
from api_client import api_client
from handlers.auth import get_auth_handler
from config import BOT_TOKEN


async def debug_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Отладочный обработчик для всех сообщений """
    print(f"DEBUG UPDATE: {update}")
    print(f"DEBUG CONTEXT: {context}")
    print(f"DEBUG USER_DATA: {context.user_data}")

async def start(update, context):
    """ Команда /start - проверяем авторизацию """

    # ОЧИСТКА: сбрасываем все предыдущие состояния
    context.user_data.clear()

    telegram_id = update.effective_user.id

    result = api_client.check_telegram_user(telegram_id)

    if result.get('exists'):
        user = result['user']
        await update.message.reply_text(
            f"✅ Добро пожаловать,  {user['first_name'] or user['nickname']}!\n\n"
            # f"You are logged in as {user['email']}\n\n"
            # f"Available commands:\n"
            # f"/batch - work with batches\n"
            # f"/test - take tests\n"
            # f"/maintenance - equipment maintenance\n"
            # f"/coa - get COA\n"
            #f"/menu - меню"
        )
    else:
        await update.message.reply_text(
            "👋 Добро пожаловать в бота приложения Family Planner!\n\n"
            "Используйте команду /auth, чтобы авторизоваться и получить полный доступ к функционалу бота."
        )

def main_with_restart():
    """ Запуск бота с автоматическим перезапуском при ошибках """
    max_restarts = 5
    restart_delay = 10  # секунд

    for attempt in range(max_restarts):
        try:
            token = BOT_TOKEN

            app = (
                ApplicationBuilder()
                .token(token)
                .read_timeout(30)
                .write_timeout(30)
                .connect_timeout(30)
                .pool_timeout(30)
                .build()
            )

            # Сначала отладочный обработчик (временно)
            app.add_handler(MessageHandler(filters.ALL, debug_update), group=1)

            # Добавляем обработчики
            app.add_handler(get_auth_handler())
            app.add_handler(CommandHandler("start", start))

            print(f"🚀 Запуск бота (попытка {attempt + 1})...")

            app.run_polling(
                poll_interval=1.0,
                timeout=30,
                drop_pending_updates=True
            )

        except (TimedOut, NetworkError) as e:
            print(f"⚠️ Сетевая ошибка: {e}")
            if attempt < max_restarts - 1:
                print(f"🔄 Перезапуск через {restart_delay} секунд...")
                time.sleep(restart_delay)
            else:
                print("❌ Достигнут лимит перезапусков")
                sys.exit(1)

        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main_with_restart()