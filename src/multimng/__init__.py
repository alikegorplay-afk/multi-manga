__all__ = [
    "MultiManga",
    "AsyncMultiManga"
]

from inspect import iscoroutinefunction as is_async
from abc import ABC, abstractmethod
from pathlib import Path

from .service import MangaManager, AsyncMangaManager
from .service.manga_service import BaseManager
from .core.mngparser import MangaParser
from .models import WorkManga, AsyncWorkManga
from ._http import HasRequest
from .config import config

logger = config.logger("multi-manga")

class BaseMultiManga(ABC):
    def __init__(
        self,
        manga_manager: BaseManager,
        session: HasRequest,
        *,
        base_url: str = None,
        max_try: int = None,
        max_workers: int = None,
    ):  
        self._session = session
        self._max_try = config.MAX_TRY if not max_try else max_try
        self._base_url = config.BASE_URL if not base_url else base_url
        self._max_worker = config.MAX_WORKERS if not max_workers else max_workers
        self.manager: BaseManager = manga_manager(
            self._session,
            config.MAX_WORKERS,
            self._max_try,
            MangaParser(self._base_url),
            self._base_url
        )
    
    @abstractmethod
    def get_info(self, url: str) -> WorkManga: ...
    
    @abstractmethod
    def download_manga(self, manga: WorkManga, path: Path | str) -> None: ...
    
class MultiManga(BaseMultiManga):
    def __init__(
        self,
        session: HasRequest,
        *,
        base_url: str = None,
        max_try: int = None,
        max_workers: int = None
    ):
        super().__init__(MangaManager, session, base_url=base_url, max_try=max_try, max_workers=max_workers)
        if is_async(session.request):
            raise TypeError("Данный класс не поддерживает асинхронность")
    
    def get_info(self, url) -> WorkManga:
        return self.manager.get_info(url)  
    
    def download_manga(self, manga, path):
        self.manager.download(manga, path)
        
class AsyncMultiManga(BaseMultiManga):
    
    def __init__(
        self,
        session: HasRequest,
        *,
        base_url: str = None,
        max_try: int = None,
        max_workers: int = None
    ):
        super().__init__(AsyncMangaManager, session, base_url=base_url, max_try=max_try, max_workers=max_workers)
        if hasattr(session, "__aenter__"):
            ...
        elif is_async(session.request):
            ...
        else:
            raise TypeError("Данный класс не поддерживает асинхронность")
    
    async def get_info(self, url: str) -> AsyncWorkManga:
        return await self.manager.get_info(url)  
    
    async def download_manga(self, manga: AsyncMangaManager, path):
        await self.manager.download(manga, path)