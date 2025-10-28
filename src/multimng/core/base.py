from abc import ABC, abstractmethod
from urllib.parse import urljoin
from typing import Any, Literal, overload, List

from bs4 import Tag, BeautifulSoup, _IncomingMarkup

from ..models import WorkManga, AsyncWorkManga
from ..config import config

logger = config.logger(__name__)

class BaseParser:
    def __init__(
        self,
        base_url: str,
        engine: str = 'html.parser'
    ):
        self._engine = engine
        self._base_url = base_url
        
    def _safe_extract_url(self, tag: Tag, attr: str, default: Any = None) -> str:
        if (not tag) or (not attr):
            logger.warning("Один из атрибутов пуст")
            return default
        
        if url := tag.get(attr):
            logger.debug(f"Найден URL: {url}")
            return urljoin(self._base_url, url)
        
        logger.warning("URL не был обнаружен")
        return default
    
class BaseMangaParser(BaseParser):
    @overload
    def parse_manga(self, data: _IncomingMarkup, manga_type: Literal["sync"]) -> WorkManga: ...
    @overload
    def parse_manga(self, data: _IncomingMarkup, manga_type: Literal["async"]) -> AsyncWorkManga: ...
    
    def parse_manga(self, data: _IncomingMarkup, manga_type: Literal["sync", "async"]) -> AsyncWorkManga | WorkManga:
        logger.info(f"Начало извлечение данных тип {manga_type}")
        if manga_type not in ["sync", "async"]:
            error_txt = f"Неподдерживаемый тип: {manga_type}"
            logger.warning(error_txt)
            raise TypeError(error_txt)
        
        soup = BeautifulSoup(data, self._engine)
        
        data = {
            "title": self._extract_title(soup),
            "url": self._extract_url(soup),
            "poster": self._extract_poster(soup),
            "gallery": self._extract_gallery(soup),
            "author": self._extract_author(soup),
            "language": self._extract_language(soup),
            "genres": self._extract_genres(soup)
        }
        
        return (
            AsyncWorkManga(**data) 
            if manga_type == 'async'
            else WorkManga(**data)
        )
        
        
        
    @abstractmethod
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Достаёт название тайтла"""
        logger.debug("Извлечение названия тайтла")
    
    @abstractmethod
    def _extract_url(self, soup: BeautifulSoup) -> str:
        """Достаёт полный URL тайтла"""
        logger.debug("Извлечение URL тайтла")
    
    @abstractmethod
    def _extract_poster(self, soup: BeautifulSoup) -> str:
        """Достаёт постер тайтла"""
        logger.debug("Извлечение постера тайтла")
    
    @abstractmethod
    def _extract_gallery(self, soup: BeautifulSoup) -> str:
        """Достаёт всю галерею тайтла"""
        logger.debug("Извлечение галереи тайтла")
    
    @abstractmethod
    def _extract_genres(self, soup: BeautifulSoup) -> List[str]:
        """Достаёт все жанры тайтла"""
        logger.debug("Извлечение жанров тайтла")
    
    @abstractmethod
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Достаёт автора тайтла"""
        logger.debug("Извлечение автора тайтла")
    
    @abstractmethod
    def _extract_language(self, soup: BeautifulSoup) -> str:
        """Достаёт язык тайтла"""
        logger.debug("Извлечение языка тайтла")