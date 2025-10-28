# MultiMangaParser

Парсер для простой работы с сайтом [multi-manga](https://multi-manga.today) имеет базовый функционал (`get_info`, `download`)

## Преимущества:
- **Универсальность** — поддержка асинхронной и синхронной версий.
- **Поддерживаемость** — чистый и структурированный код.
- **Гибкость** — поддержка aiohttp, httpx, requests, urlib3 и тп.

## Быстрый старт
1. **Установить репозиторий:**
```cmd
pip install git+https://github.com/alikegorplay-afk/multi-manga.git
```
2. **Установить необходимости:**
```cmd
pip install requirements.txt
```
3.**Установить любой HTTP клент**
```cmd
pip install requests # Но можно и httpx, aiohttp, urlib3...
```
4. **Использовать:**
```python
from multimng import MultiManga
import requests

api = MultiManga(requests.session())
result = api.get_info("https://multi-manga.today/15636-moja-sosedka-golodnaja-milfa-gokinjou-san-wa-ueta-hitozuma.html")
```