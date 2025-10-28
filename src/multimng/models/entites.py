__all__ = [
    "MiniManga",
    "Manga",
    "WorkManga",
    "AsyncWorkManga",
]

import json
import os
import asyncio

from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
from typing import List, Optional, Awaitable
from pathlib import Path

import aiofiles

from .._http import HasRequest, BaseHttpManager, HTTPError
from .._http import is_async
from ..config import config

logger = config.logger(__name__)

@dataclass
class MiniManga:
    """Хранит базовую ифнормацию об тайтле"""
    title: str
    url: str
    poster: str
    
    @property
    def id(self):
        return self.url.split("/")[-1].split('-')[0]
    
    
@dataclass
class Manga(MiniManga):
    """Хранит полную ифнормацию об тайтле"""
    gallery: List[str]
    
    author: Optional[str] = field(default=None)
    language: Optional[str] = field(default=None)
    genres: List[str] = field(default_factory=list)
    
class BaseManga(Manga, ABC):
    def save_as_json(self, path: Path | str) -> None:
        """save_as_json - Сохраняет данные в виде Json

        Args:
            path (Path | str): Путь для сохранения json файла
        """
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(
                asdict(self),
                file
            )
    @abstractmethod
    def _download_img(self, url: str, path: Path | str, session: BaseHttpManager, *, max_try: int = config.MAX_TRY) -> None:
        """Скачивает фотографию

        Args:
            url (str): Сама фотография
            path (Path | str): Путь к файлу
            max_try (int): Максимальное количество попыток
            session (BaseHttpManager): HttpManager для скачивание
        """
        
    @abstractmethod
    def download(self, path: Path | str, session: HasRequest | BaseHttpManager, *, max_workers: int = 5):
        """download Скачивает всю галлерею из gallery

        Args:
            path (Path | str): Директория для скачивание файла
            session (HasRequest | BaseHttpManager): Сессия HTTP библиотеки либо нащ кастомный класс
            max_workers (int, optional): Максимальное количество потоков для работы. Defaults to 5.
        """

    def convert(self) -> MiniManga:
        """Конвертирует в маленькую версию

        Returns:
            MiniManga: Маленькая версия
        """
        return MiniManga(
            title = self.title,
            url = self.url,
            poster = self.poster
        )
        
    @staticmethod
    def _get_name(url: str) -> str:
        """Вспомогательная функция что-бы достать название файла"""
        url_parsed = urlparse(url)
        return os.path.basename(url_parsed.path)
    

@dataclass
class WorkManga(BaseManga):
    """Хранит полную ифнормацию об тайтле"""
    def download(self, path: Path | str, session, *, max_workers: int = 5):
        if isinstance(session, BaseHttpManager):
            ...
        elif is_async(session.request):
            raise TypeError("Переданная сессия не является синхронной")
        
        path = Path(path)
        http = BaseHttpManager(session)
        
        path.mkdir(parents=True, exist_ok=True)
        
        tasks = self._make_tasks(path, http)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(lambda x: self._download_img(*x), tasks)
            
    def _download_img(self, url, path, session, *, max_try = config.MAX_TRY):
        logger.debug(f"Попытка скачать файл: {url}, по пути: {path} максимальное количество попыток: {max_try}")
        if os.path.exists(path):
            logger.warning(f"Объект: {path} уже существует")
            return
        
        with open(path, 'wb') as f:
            for try_num in range(1, max_try + 1):
                logger.debug(f"{try_num}. Попытка скачать: {url}")
                try:
                    f.write(session._sync_get_content(url, headers = {}))
                    return
                except Exception as e:
                    logger.warning(f"{try_num}. Ошибка при попытке скачать {url}: {e}")
                    
            logger.critical(f"Не получилось скачать: {url}")
            raise HTTPError(f"Не удалось скачать файл: {url}")
    
    def _make_tasks(self, path: Path, http: BaseHttpManager):
        """Вспомогательная функция что-бы создать задачи"""
        tasks = []
        for img_url in self.gallery:
            if not (name := self._get_name(img_url)):
                logger.warning(f"{img_url} не является файлом")
                continue
            file_path = path / name
            tasks.append((img_url, file_path, http))
        return tasks


class AsyncWorkManga(BaseManga):
    async def _download_img(
        self, 
        url: str,
        path: Path | str,
        session: BaseHttpManager,
        semaphore: asyncio.Semaphore,
        *,
        max_try = config.MAX_TRY
    ):
        """Скачивает фотографию

        Args:
            url (str): Сама фотография
            path (Path | str): Путь к файлу
            max_try (int): Максимальное количество попыток
            session (BaseHttpManager): HttpManager для скачивание
            semaphore (asyncio.Semaphore): semaphore для ограничение потоков
        """
        logger.debug(f"Попытка скачать файл: {url}, по пути: {path} максимальное количество попыток: {max_try}")
        if os.path.exists(path):
            logger.warning(f"Объект: '{path}' уже существует")
            return
        
        async with semaphore:
            async with aiofiles.open(path, 'wb') as f:
                for try_num in range(1, max_try + 1):
                    logger.debug(f"{try_num}. Попытка скачать: {url}")
                    try:
                        await f.write(await session._async_get_content(url))
                        return
                    except Exception as e:
                        logger.warning(f"{try_num}. Ошибка при попытке скачать {url}: {e}")
            logger.critical(f"Не получилось скачать: {url}")
            raise HTTPError(f"Не удалось скачать файл: {url}")
    
    async def download(self, path, session, *, max_workers = 5):
        if isinstance(session, BaseHttpManager):
            ...
        elif not is_async(session.request):
            raise TypeError("Переданная сессия не является асинхронной")
        
        path = Path(path)
        http = BaseHttpManager(session)
        semaphore = asyncio.Semaphore(max_workers)
        
        path.mkdir(parents=True, exist_ok=True)
        
        await asyncio.gather(
            *self._make_tasks(path, http, semaphore)
        )
        
    def _make_tasks(
        self,
        path: Path | str,
        session: BaseHttpManager,
        semaphore: asyncio.Semaphore
    ) -> List[Awaitable]:
        tasks = []
        for img_url in self.gallery:
            if not (name := self._get_name(img_url)):
                logger.warning(f"{img_url} не является файлом")
                continue
            
            file_path = path / name
            tasks.append(
                asyncio.create_task(
                    self._download_img(img_url, file_path, session, semaphore)
                )
            )
        return tasks