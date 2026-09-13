import os
import requests

# Создаем папку
os.makedirs("media", exist_ok=True)

# Прямые ссылки на красивые тематические фото с Unsplash (в высоком качестве)
images = {
    "tolstoy.jpg": "https://images.unsplash.com/photo-1455390582262-044cdead27d8",
    "science.jpg": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb",
    "news.jpg": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9",
    "manual.jpg": "https://images.unsplash.com/photo-1585659722983-39cb3ee79623",
}

# Добавляем User-Agent, чтобы имитировать браузер
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("Скачиваю красивые картинки...")
for filename, url in images.items():
    print(f"Загрузка {filename}...")
    try:
        # Делаем запрос с заголовками
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Проверяем успешность
        
        # Сохраняем файл
        with open(f"media/{filename}", 'wb') as f:
            f.write(response.content)
        print(f"  ✓ {filename} загружен")
    except Exception as e:
        print(f"  ✗ Ошибка при загрузке {filename}: {e}")

print("\nКартинки успешно сохранены в папку media!")