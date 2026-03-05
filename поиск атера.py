import requests

# Твой API токен
API_TOKEN = "WE5F7TA-CBS4MEF-MBENDVR-Z31P1H5"
HEADERS = {"X-API-KEY": API_TOKEN}
BASE_URL = "https://api.poiskkino.dev/v1.4"


def find_actor_movies():
    """
    ПРОСТОЙ И РАБОЧИЙ поиск фильмов актера
    """
    print("\n🎬 ПОИСК ФИЛЬМОВ АКТЕРА")
    print("=" * 50)

    # Вводим имя
    name = input("Введите имя актера: ").strip()

    if not name:
        print("❌ Введи нормально имя")
        return

    print(f"\n🔍 Ищем: {name}")

    # ПРОСТОЙ ЗАПРОС - ищем по имени
    url = f"{BASE_URL}/person/search?page=1&limit=20&query={name}"
    params = {
        "query": name,
        "page":1,
        "limit": 20
    }

    try:
        print(url,HEADERS,params)
        response = requests.get(url, headers=HEADERS)
        print(response.json())
        if response.status_code != 200:
            print(f"❌ Ошибка {response.status_code}")
            return

        data = response.json()
        actors = data.get('docs', [])

        if not actors:
            print("❌ Никого не нашли")
            return


        # Если нашли несколько актеров
        if len(actors) > 1:
            print("\nНайдено несколько актеров:")
            for i, actor in enumerate(actors[:5], 1):
                ru_name = actor.get('name', '')
                en_name = actor.get('enName', '')
                display = ru_name if ru_name else en_name
                print(f"{i}. {display}")

            choice = input("\nВыбери номер (или Enter - первый): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(actors):
                selected = actors[int(choice) - 1]
            else:
                selected = actors[0]
        else:
            selected = actors[0]

        actor_id = selected['id']
        actor_name = selected.get('name') or selected.get('enName', 'Актер')

        print(f"\n✅ Выбрал: {actor_name}")
        print(f"🆔 ID: {actor_id}")

        # Ищем фильмы актера
        print("\n🔎 Ищу фильмы...")

        movies_url = f"{BASE_URL}/movie"
        movies_params = {
            "persons.id": actor_id,
            "limit": 250,
            "selectFields": ["name", "year", "rating"]
        }

        movies_response = requests.get(movies_url, headers=HEADERS, params=movies_params)

        if movies_response.status_code != 200:
            print("❌ Не могу найти фильмы")
            return

        movies_data = movies_response.json()
        movies = movies_data.get('docs', [])

        if not movies:
            print("❌ У этого актера нет фильмов в базе")
            return

        # Выводим фильмы
        print(f"\n🎬 ФИЛЬМЫ ({len(movies)} шт.):")
        print("-" * 50)

        # Сортируем по году
        movies_sorted = sorted(movies, key=lambda x: x.get('year', 0), reverse=True)

        for i, movie in enumerate(movies_sorted[:30], 1):  # Покажем первые 30
            title = movie.get('name', 'Без названия')
            year = movie.get('year', '----')
            rating = movie.get('rating', {}).get('kp', '?')
            if rating != '?' and rating:
                rating = f"{rating:.1f}"

            print(f"{i:2}. {title[:40]:40} {year}  ★ {rating}")

        if len(movies) > 30:
            print(f"\n... и еще {len(movies) - 30} фильмов")

        # Сохраняем в файл
        save = input("\n💾 Сохранить в файл? (да/нет): ").lower()
        if save in ['да', 'д', 'yes', 'y']:
            filename = f"{actor_name.replace(' ', '_')}_фильмы.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Фильмы с {actor_name}\n")
                f.write(f"Всего: {len(movies)}\n")
                f.write("=" * 50 + "\n")
                for i, m in enumerate(movies_sorted, 1):
                    title = m.get('name', 'Без названия')
                    year = m.get('year', '----')
                    f.write(f"{i}. {title} ({year})\n")
            print(f"✅ Сохранил в {filename}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


# Запуск
if __name__ == "__main__":
    while True:
        find_actor_movies()
        again = input("\n🔄 Еще? (да/нет): ").lower()
        if again not in ['да', 'д', 'yes', 'y']:
            print("👋 Пока!")
            break