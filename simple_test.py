import requests

TOKEN = "859EJFM-R0HMPJK-Q038VE6-QMXJVWP"
headers = {"X-API-KEY": TOKEN}

# Тест 1: Простой запрос
print("Тест 1: Простой запрос")
response = requests.get(
    "https://api.kinopoisk.dev/v1.4/movie/447301",
    headers=headers
)
print(f"Статус: {response.status_code}")
if response.status_code == 200:
    print("✅ Токен работает!")
    print(f"Фильм: {response.json().get('name')}")
else:
    print(f"❌ Ошибка: {response.text}")

print("\n" + "="*50 + "\n")

# Тест 2: Запрос со случайными параметрами
print("Тест 2: Запрос со случайными параметрами")
response2 = requests.get(
    "https://api.kinopoisk.dev/v1.4/movie",
    headers=headers,
    params={
        "page": 1,
        "limit": 5,
        "type": "movie",
        "notNullFields": ["name", "poster.url", "description"]
    }
)
print(f"Статус: {response2.status_code}")
if response2.status_code == 200:
    data = response2.json()
    movies = data.get("docs", [])
    print(f"Найдено фильмов: {len(movies)}")
    if movies:
        print(f"Первый фильм: {movies[0].get('name')}")
else:
    print(f"❌ Ошибка: {response2.text}")