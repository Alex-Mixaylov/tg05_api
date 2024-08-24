import os
import requests
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import asyncio

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение токена телеграм-бота и API-ключа из переменных окружения
WINE_BOT_TOKEN = os.getenv('WINE_BOT_TOKEN')
WINE_API_KEY = os.getenv('WINE_API_KEY')

# Инициализация бота и диспетчера
bot = Bot(token=WINE_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# URL для отправки запросов на распознавание винных этикеток
RECOGNITION_API_URL = "https://wine-recognition2.p.rapidapi.com/v1/results"
HEADERS = {
    "x-rapidapi-key": WINE_API_KEY,
    "x-rapidapi-host": "wine-recognition2.p.rapidapi.com",
    "Content-Type": "multipart/form-data"
}

# Проверка и создание директории tmp
if not os.path.exists("tmp"):
    os.makedirs("tmp")

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Отправь мне изображение винной этикетки, и я попробую распознать её.")


# Обработчик загрузки изображений
@dp.message(F.content_type == types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    # Получение объекта фотографии
    photo = message.photo[-1]  # Берем изображение с максимальным разрешением

    # Загрузка фото на локальный диск
    photo_path = f"tmp/{photo.file_id}.jpg"
    await bot.download(photo, destination=photo_path)

    # Отправка фото на распознавание
    result = await recognize_wine(photo_path)

    # Ответ пользователю
    if result:
        await message.answer(f"Распознано: {result}")
    else:
        await message.answer("Извините, не удалось распознать винную этикетку. Попробуйте другое изображение.")


async def recognize_wine(image_path):
    # Чтение изображения
    with open(image_path, "rb") as image_file:
        files = {'file': image_file}

        # Отправка запроса к API
        loop = asyncio.get_event_loop()  # Получаем текущий event loop
        response = await loop.run_in_executor(None, lambda: requests.post(RECOGNITION_API_URL, headers=HEADERS, files=files))

        # Обработка ответа
        if response.status_code == 200:
            data = response.json()
            # Извлечение наиболее вероятного результата
            try:
                wine_name = list(data['results'][0]['entities'][0]['classes'].keys())[0]
                return wine_name
            except (KeyError, IndexError):
                return None
        else:
            logging.error(f"Ошибка при запросе: {response.status_code} {response.text}")
            return None


async def main():
    # Запуск polling внутри асинхронного контекста
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
