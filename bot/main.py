import sys
import time

from telegram import Update
from telegram.error import TimedOut, NetworkError
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes, MessageHandler, filters

from handlers.support import get_support_handlers
from handlers.menu import get_menu_handlers
from handlers.events import get_add_event_handler
from handlers.auth import get_auth_handler
from config import BOT_TOKEN


async def debug_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Отладочный обработчик для всех сообщений """
    print(f"DEBUG UPDATE: {update}")
    print(f"DEBUG CONTEXT: {context}")
    print(f"DEBUG USER_DATA: {context.user_data}")


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
                .read_timeout(60)
                .write_timeout(60)
                .connect_timeout(60)
                .pool_timeout(60)
                .build()
            )

            # Сначала отладочный обработчик (временно)
            app.add_handler(MessageHandler(filters.ALL, debug_update), group=1)

            # Добавляем обработчики
            app.add_handler(get_add_event_handler())
            app.add_handler(get_auth_handler())

            # Регистрируем обработчики раздела поддержки
            for handler in get_support_handlers():
                app.add_handler(handler)

            # Регистрируем обработчики меню
            for handler in get_menu_handlers():
                app.add_handler(handler)

            print(f"🚀 Запуск бота (попытка {attempt + 1})...")

            app.run_polling(
                poll_interval=1.0,
                timeout=60,
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