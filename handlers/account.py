from aiogram import types
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from state import Form
from keyboards.account_kb import account_kb, finans_kb, settings_kb
from keyboards.main_menu import inline_keyboard

# Создаем роутер
account_router = Router()

# Обработчик для кнопки "Аккаунт"
@account_router.callback_query(lambda c: c.data == "account")
async def account_handler(callback: types.CallbackQuery, state: FSMContext):
    # Убираем "часики" у кнопки
    await callback.answer()

    # Отправляем сообщение с клавиатурой для аккаунта
    await callback.message.edit_text("Добро пожаловать в аккаунт", reply_markup=account_kb)
    await state.set_state(Form.account)

# Обработчик для кнопки "Финансы"
@account_router.callback_query(lambda c: c.data == "finans")
async def finans_handler(callback: types.CallbackQuery, state: FSMContext):
    # Убираем "часики" у кнопки
    await callback.answer()

    # Отправляем сообщение с клавиатурой для финансов
    await callback.message.edit_text("Добро пожаловать в раздел 'Финансы'", reply_markup=finans_kb)
    await state.set_state(Form.finans)

# Обработчик для кнопки "Настройки"
@account_router.callback_query(lambda c: c.data == "settings")
async def settings_handler(callback: types.CallbackQuery, state: FSMContext):
    # Убираем "часики" у кнопки
    await callback.answer()

    # Отправляем сообщение с клавиатурой для настроек
    await callback.message.edit_text("Добро пожаловать в раздел 'Настройки'", reply_markup=settings_kb)
    await state.set_state(Form.settings)

@account_router.callback_query(lambda c: c.data == "exit_to_menu")
async def exit_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Вы вернулись в главное меню.", reply_markup=inline_keyboard)
    await state.set_state(Form.menu)