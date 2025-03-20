from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Клавиатура для аккаунта
account_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Финансы", callback_data="finans"), InlineKeyboardButton(text="Настройки", callback_data="settings")],
    [InlineKeyboardButton(text="Выход в меню", callback_data="exit_to_menu")]  # Добавляем кнопку "Выход в меню"
])

# Клавиатура для финансов
finans_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Баланс", callback_data="balance")],
    [InlineKeyboardButton(text="Мои карты", callback_data="my_cards")],
    [InlineKeyboardButton(text="Пополнить", callback_data="replenish")],
    [InlineKeyboardButton(text="Выход в меню", callback_data="exit_to_menu")]  # Добавляем кнопку "Выход в меню"
])

# Клавиатура для настроек
settings_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Обращение", callback_data="appeal"), InlineKeyboardButton(text="Справка", callback_data="reference")],
    [InlineKeyboardButton(text="Выход в меню", callback_data="exit_to_menu")]  # Добавляем кнопку "Выход в меню"
])