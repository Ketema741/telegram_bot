from aiogram import Bot
from os import getenv
from dotenv import load_dotenv
from aiogram.enums import ParseMode
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)


    