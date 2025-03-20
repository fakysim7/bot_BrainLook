from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Аккаунт", callback_data="account"), InlineKeyboardButton(text="События", callback_data="events")],
    [InlineKeyboardButton(text="Последние места", callback_data="last_location"), InlineKeyboardButton(text="Бизнес ассистент", callback_data="business_assistant")]
])

