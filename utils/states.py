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

class DialogStates(StatesGroup):
    waiting_for_event_data = State() 
