# handlers/messages.py
from aiogram import Router
from aiogram.types import Message
from AI.gpt import get_gpt_response

messages_router = Router()

@messages_router.message()
async def handle_message(message: Message):
    user_message = message.text
    response = get_gpt_response(user_message)
    await message.reply(response)