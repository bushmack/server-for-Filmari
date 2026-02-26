import requests

token = "WE5F7TA-CBS4MEF-MBENDVR-Z31P1H5"
headers = {"X-API-KEY": token}

# Тест 1: тот самый фильм который работал
r1 = requests.get("https://api.kinopoisk.dev/v1.4/movie/447301", headers=headers)
print(f"Фильм по ID: {r1.status_code}")

# Тест 2: поиск фильмов
r2 = requests.get("https://api.kinopoisk.dev/v1.4/movie", headers=headers, params={"page": 1, "limit": 1})
print(f"Поиск фильмов: {r2.status_code}")

# Тест 3: случайные
r3 = requests.get("https://api.kinopoisk.dev/v1.4/movie/random", headers=headers)
print(f"Случайный: {r3.status_code}")