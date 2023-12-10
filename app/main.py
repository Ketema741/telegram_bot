import asyncio
import logging
import sys

from aiogram import Dispatcher
from bot.handlers.registration_handler import form_router
from bot.bot_instance import bot

async def main():
    logging.basicConfig(level=logging.INFO)
    
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())