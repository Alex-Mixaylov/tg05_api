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
    "x-rapidapi-host": "wine-recognition2.p.rapidapi.com"
}

# Проверка и создание директории tmp, если она не существует
if not os.path.exists("tmp"):
    os.makedirs("tmp")


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Отправь мне изображение винной этикетки, и я попробую распознать её.")


# Обработчик загрузки изображений
@dp.message(F.content_type == types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    # Получение объекта фотографии с максимальным разрешением
    photo = message.photo[-1]

    # Получение информации о файле и генерация пути для сохранения
    file_info = await bot.get_file(photo.file_id)
    file_extension = os.path.splitext(file_info.file_path)[1]  # Получаем расширение файла (.jpg или .png)
    photo_path = f"tmp/{photo.file_id}{file_extension}"

    # Скачивание фото на локальный диск
    await bot.download(photo, destination=photo_path)

    # Отправка фото на распознавание
    result = await recognize_wine(photo_path)

    # Ответ пользователю
    if result:
        await message.answer(result)
    else:
        await message.answer("Извините, не удалось распознать винную этикетку. Попробуйте другое изображение.")


async def recognize_wine(image_path):
    # Открытие файла изображения для чтения
    with open(image_path, "rb") as image_file:
        # Отправка запроса к API с использованием правильного имени поля "image"
        files = {
            "image": image_file  # Поле должно называться "image"
        }

        # Отправка запроса на распознавание изображения
        response = requests.post(RECOGNITION_API_URL, headers=HEADERS, files=files)

        # Обработка ответа
        if response.status_code == 200:
            data = response.json()
            try:
                # Получение списка наименований вин с вероятностями
                wine_classes = data['results'][0]['entities'][0]['classes']
                results = []

                # Ограничиваем количество вариантов до 3 и пронумеровываем их
                for idx, (wine_name, probability) in enumerate(wine_classes.items()):
                    if idx >= 3:  # Выводим только первые 3 варианта
                        break
                    probability_percent = probability * 100
                    results.append(f"{idx + 1}) Это вино {wine_name} с вероятностью {probability_percent:.2f}%")

                # Возвращаем результат в виде строки, разделенной новой строкой
                return "\n".join(results)
            except (KeyError, IndexError):
                return None
        else:
            logging.error(f"Ошибка при запросе: {response.status_code} {response.text}")
            return None


async def main():
    # Запуск polling в асинхронном контексте
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
