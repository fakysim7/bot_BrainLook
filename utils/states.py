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
    collecting_data = State()  
    waiting_for_title = State()  
    waiting_for_date = State()   
    waiting_for_time = State()   
    waiting_for_place = State()  
    waiting_for_type = State()   
    waiting_for_guests = State()

