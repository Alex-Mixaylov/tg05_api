import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import random

from dotenv import load_dotenv
import os

import logging

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Вот в этом промежутке мы будем работать и писать новый код

async def main():
   await dp.start_polling(bot)

if __name__ == '__main__':
   asyncio.run(main())