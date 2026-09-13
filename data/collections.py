# data/collections.py

publications = [
    {
        "id": 1,
        "title": "Отрывок из романа 'Война и мир'",
        "genre": "Художественный",
        "avg_length": 1500, # Средняя длина (в словах)
        "unique_words_share": "42%", # Доля уникальных слов
        "description": "Классическое произведение Л.Н. Толстого с длинными и сложными для восприятия предложениями.",
        "image_url": "http://localhost:9000/readability/tolstoy.jpg",
        "video_url": "http://localhost:9000/readability/tolstoy.mp4",
        "status": "опубликован",
        "likes": [101, 102, 105]
    },
    {
        "id": 2,
        "title": "Статья по квантовой физике",
        "genre": "Научный",
        "avg_length": 850,
        "unique_words_share": "68%",
        "description": "Сухой научный текст, изобилующий сложными физическими терминами и формулами.",
        "image_url": "http://localhost:9000/readability/science.jpg",
        "video_url": "http://localhost:9000/readability/science.mp4",
        "status": "опубликован",
        "likes": [101]
    },
    {
        "id": 3,
        "title": "Новость о выходе смартфона",
        "genre": "Публицистический",
        "avg_length": 320,
        "unique_words_share": "55%",
        "description": "Легкая новостная заметка, написанная для широкого круга читателей.",
        "image_url": "http://localhost:9000/readability/news.jpg",
        "video_url": "http://localhost:9000/readability/news.mp4",
        "status": "черновик",
        "likes": []
    },
    {
        "id": 4,
        "title": "Инструкция к СВЧ-печи",
        "genre": "Технический",
        "avg_length": 150,
        "unique_words_share": "30%",
        "description": "Краткое и сухое описание функций бытового прибора.",
        "image_url": "http://localhost:9000/readability/manual.jpg",
        "video_url": "http://localhost:9000/readability/manual.mp4",
        "status": "удален",
        "likes": [102, 103, 109]
    }
]