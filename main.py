import asyncio
import logging
import sys
from typing import Any
from os import getenv

from aiogram import F, Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
dp = Dispatcher()
router1 = Router()


@router1.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {hbold(message.from_user.full_name)} 🎊 Welcome, and enjoy your stay!!")

@router1.message(Command("help"))
async def help_command(message: types.Message):
    await message.reply("This is the help message from A2SV bot")

@router1.message(F.text == 'hello world')
async def my_handler(message: Message) -> Any:
    return message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@router1.message(Command("hello_world"))
async def handle_hellow_world(message: Message):
    await message.answer("Hello! Welcome to the bot.")

@router1.message()
async def echo_handler(message: types.Message) -> None:
    try:
        await message.copy_to(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")

async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    dp.include_router(router1)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
