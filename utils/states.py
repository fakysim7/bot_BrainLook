from aiogram.fsm.state import StatesGroup, State

class EventState(StatesGroup):
    WAITING_FOR_NAME = State()
    WAITING_FOR_YEAR = State()
    WAITING_FOR_MONTH = State()
    WAITING_FOR_DAY = State()
    WAITING_FOR_TIME = State()
    WAITING_FOR_CUSTOM_TIME = State()
    WAITING_FOR_DESCRIPTION = State()

class ProfileStates(StatesGroup):
    change_age = State()  
    change_workplace = State()  

class Registration(StatesGroup):
    age = State()
    workplace = State()


class EventCreationStates(StatesGroup):
    waiting_for_title = State()  # Ожидание названия события
    waiting_for_date = State()   # Ожидание даты
    waiting_for_time = State()   # Ожидание времени
    waiting_for_place = State()  # Ожидание места
    waiting_for_type = State()   # Ожидание типа события
    waiting_for_guests = State() # Ожидание списка гостей
