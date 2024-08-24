import requests

url = "https://photomath1.p.rapidapi.com/maths/solve-problem"  # Укажите правильный endpoint

# Открываем изображение для отправки
with open("foto/IMG_9414.jpg", "rb") as image_file:
    files = {"file": image_file}

    headers = {
        "x-rapidapi-key": "f115209b4cmsh517b193399e84d0p164af3jsndbe9e171d02b",
        "x-rapidapi-host": "photomath1.p.rapidapi.com"
    }

    # Отправляем POST запрос с файлом изображения
    response = requests.post(url, files=files, headers=headers)

    # Выводим JSON ответ
    print(response.json())
