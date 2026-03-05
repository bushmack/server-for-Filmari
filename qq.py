
import httpx

async def _make_request(self, endpoint: str, params: dict = None) -> dict:
    """Базовый метод для запросов к API"""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            url = f"{self.base_url}{endpoint}"
            print(f"Запрос к: {url}")

            response = await client.get(
                url,
                headers=self.headers,
                params=params
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Ошибка API: {response.status_code}")
                return {"docs": []}
    except Exception as e:
        print(f"Ошибка запроса: {e}")
        return {"docs": []}

async def search_by_name(self, query: str, limit: int = 20) -> List[dict]:
    """Поиск фильмов по названию"""
    cache_key = f"name_{query}_{limit}"

    cached = self.search_cache.get(cache_key)
    if cached:
        return cached

    print(f"\n🔍 Поиск по названию: '{query}'")

    if len(query) < 2:
        return []

    params = {
        "page": 1,
        "limit": limit,
        "query": query,
        "selectFields": ["id", "name", "description", "year", "rating",
                         "poster", "genres", "countries", "movieLength",
                         "type", "ageRating", "alternativeName"],
        "notNullFields": ["poster.url", "description"]
    }

    data = await self._make_request("/person/search", params)

    if not data or not data.get('docs'):
        print(f"  Ничего не найдено для '{query}'")
        return []

    content_list = data.get('docs', [])
    print(f"  Найдено фильмов в ответе: {len(content_list)}")

    matching_content = []
    query_lower = query.lower().strip()

    for content in content_list:
        if content.get('id') and content.get('name'):
            content_title = content.get('name', '').lower().strip()
            if content_title == query_lower or query_lower in content_title:
                matching_content.append(content)

    matching_content = matching_content[:limit]

    print(f"  После фильтрации: {len(matching_content)} фильмов")

    if not matching_content:
        return []

    result = [self._convert_to_wpf_format(m) for m in matching_content]
    print(f"  Возвращаем {len(result)} фильмов")

    self.search_cache.set(cache_key, result)
    return result


