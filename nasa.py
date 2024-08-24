import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import random
from datetime import datetime, timedelta

from dotenv import load_dotenv
import os

import requests
import logging

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")
NASA_API_KEY = os.getenv("NASA_API_KEY")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_random_apod():
   end_date = datetime.now()
   start_date = end_date - timedelta(days=365)
   random_date = start_date + (end_date - start_date) * random.random()
   date_str = random_date.strftime("%Y-%m-%d")
   url = f'https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&date={date_str}'
   response = requests.get(url)
   return response.json()

@dp.message(Command("random_apod"))
async def random_apod(message: Message):
   apod = get_random_apod()
   photo_url = apod['url']
   title = apod['title']
   await message.answer_photo(photo=photo_url, caption=f"{title}")
@dp.message(Command("start"))
async def start_command(message: Message):
   await message.answer("Привет! Введи команду random_apod")


async def main():
   await dp.start_polling(bot)

if __name__ == '__main__':
   asyncio.run(main())