from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_back_button(callback_data="menu_main"):
    """ Кнопка возврата в главное меню """
    return [InlineKeyboardButton("◀️ Назад в меню", callback_data=callback_data)]

def get_main_menu_keyboard():
    """ Клавиатура главного меню """
    keyboard = [
        [
            InlineKeyboardButton("📰 Новости", callback_data="section_news"),
            InlineKeyboardButton("🆘 Поддержка", callback_data="section_support")
        ],
        [
            InlineKeyboardButton("⚡ Быстрое добавление события", callback_data="section_quick_event"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_yes_no_keyboard(callback_prefix):
    """ Клавиатура подтверждения """
    keyboard = [
        [
            InlineKeyboardButton("✅ Да", callback_data=f"{callback_prefix}_yes"),
            InlineKeyboardButton("❌ Нет", callback_data=f"{callback_prefix}_no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)