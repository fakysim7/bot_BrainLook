from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from state import Form
from keyboards.main_menu import inline_keyboard
from aiogram import Router


router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await message.answer("Привет! Я твой ассистент. Выберите действие:", reply_markup=inline_keyboard)
    await state.set_state(Form.menu)

