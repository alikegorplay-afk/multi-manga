#import asyncio

from multimng import AsyncMultiManga, MultiManga
import requests
#import aiohttp
#import httpx

with requests.session() as session:
    api = MultiManga(session)
    result = api.get_info("https://multi-manga.today/15636-moja-sosedka-golodnaja-milfa-gokinjou-san-wa-ueta-hitozuma.html")

#with httpx.Client() as session:
#    api = MultiManga(session)
#    result = api.get_info("https://multi-manga.today/15636-moja-sosedka-golodnaja-milfa-gokinjou-san-wa-ueta-hitozuma.html")
#
#async def main():
#    async with httpx.AsyncClient() as session:
#        api = AsyncMultiManga(session)
#        result = await api.get_info("https://multi-manga.today/15636-moja-sosedka-golodnaja-milfa-gokinjou-san-wa-ueta-hitozuma.html")
#    
#    async with aiohttp.ClientSession() as session:
#        api = AsyncMultiManga(session)
#        result = await api.get_info("https://multi-manga.today/15636-moja-sosedka-golodnaja-milfa-gokinjou-san-wa-ueta-hitozuma.html")
#    
#asyncio.run(main())