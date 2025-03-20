from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    menu = State()  # Главное меню
    account = State()  # Состояние "Аккаунт"
    finans = State()  # Состояние "Финансы"
    settings = State()  # Состояние "Настройки"