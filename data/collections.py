services = [
    {
        "id": 1,
        "name": "Индекс Флеша",
        "description": "Оценка лёгкости восприятия текста.",
        "formula": "FRE",
        "image_url": "http://localhost:9000/readability/flesh.png",
    },
    {
        "id": 2,
        "name": "Индекс тумана Ганнинга",
        "description": "Оценка сложности текста и требуемого уровня образования.",
        "formula": "FOG",
        "image_url": "http://localhost:9000/readability/fog.png",
    },
    {
        "id": 3,
        "name": "Статистика текста",
        "description": "Количество слов, предложений, слогов и сложных слов.",
        "formula": None,
        "image_url": "http://localhost:9000/readability/statistics.png",
    },
]


application = {
    "id": 1,
    "text": (
        "Современные информационные технологии позволяют "
        "анализировать большие объёмы текстовой информации. "
        "Оценка читабельности помогает определить, насколько "
        "легко пользователь может воспринимать содержание."
    ),
    "status": "Новая",
    "comment": "Проверить текст статьи перед публикацией",
}


application_services = [
    {
        "service": services[0],
        "result": None,
    },
    {
        "service": services[1],
        "result": None,
    },
]