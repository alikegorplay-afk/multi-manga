from pathlib import Path
from abc import ABC, abstractmethod
from typing import Union

from .._http import HasRequest, BaseHttpManager
from ..models import AsyncWorkManga, WorkManga
from ..models.entites import BaseManga
from ..core.mngparser import BaseMangaParser, MangaParser
from ..config import config

logger = config.logger(__name__)

class BaseManager(ABC):
    def __init__(
        self,
        session: HasRequest,
        max_workers: int,
        max_try: int = config.MAX_TRY,
        parser: BaseMangaParser = None,
        base_url: str = config.BASE_URL,
    ):
        if parser is None:
            self._parser = MangaParser(base_url=base_url)
        elif isinstance(parser, BaseMangaParser):
            self._parser = parser
        else:
            logger.error(f"Неподдерживаемый класс парсера: {type(parser).__name__}")
            raise TypeError(f"Неподдерживаемый класс парсера: {type(parser).__name__}")
        
        self._max_workers = max_workers
        self._session = BaseHttpManager(session)
        self._max_try = max_try
        
    @abstractmethod
    def get_info(self, url: str) -> BaseManga:
        """Получает информацию о тайтле

        Args:
            url (str): URL на саму мангу

        Returns:
            BaseManga: Информация о манге
        """
        
    @abstractmethod
    def download(self, manga: BaseManga, path: Path | str) -> None:
        """Скачивает мангу

        Args:
            manga (BaseManga): Непосредственно сама манга
            path (Path | str): Директория для скачивания файла
        """


class MangaManager(BaseManager):
    """Синхронный менеджер для работы с мангой"""
    
    def get_info(self, url: str) -> WorkManga:
        response = self._session._sync_get_content(url, headers={})
        return self._parser.parse_manga(response, 'sync')
    
    def download(self, manga: WorkManga, path: Path | str) -> None:
        """Скачивает всю галерею из gallery

        Args:
            manga (WorkManga): Непосредственно сама манга
            path (Path | str): Директория для скачивания файла
        """
        manga.download(path, self._session, max_workers=self._max_workers)


class AsyncMangaManager(BaseManager):
    """Асинхронный менеджер для работы с мангой"""
    
    async def get_info(self, url: str) -> AsyncWorkManga:
        response = await self._session._async_get_content(url, headers={})
        return self._parser.parse_manga(response, 'async')
    
    async def download(self, manga: AsyncWorkManga, path: Path | str) -> None:
        """Скачивает всю галерею из gallery

        Args:
            manga (AsyncWorkManga): Непосредственно сама манга
            path (Path | str): Директория для скачивания файла
        """
        await manga.download(path, self._session, max_workers=self._max_workers)