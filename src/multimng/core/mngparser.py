from functools import lru_cache
from typing import Dict

from bs4 import BeautifulSoup

from .base import BaseMangaParser
from .errors import ParseError

from ..tools import filter_truthy
from ..config import config

logger = config.logger(__name__)

class MangaParser(BaseMangaParser):
    def _extract_title(self, soup):
        if title := soup.find('h1'):
            return title.get_text(strip=True)
        raise ParseError(f"Не найден обязательный атрибут: 'title'")
    
    def _extract_url(self, soup):
        if url := soup.select_one('link[rel="canonical"]'):
            return self._safe_extract_url(url, "href")
        
        raise ParseError(f"Не найден обязательный атрибут: 'url'")
    
    def _extract_poster(self, soup):
        if poster := soup.select_one("#cover img"):
            return self._safe_extract_url(poster, "data-src")
        
        raise ParseError(f"Не найден обязательный атрибут: 'poster'")
    
    def _extract_gallery(self, soup):
        if not (imgs := soup.select('#thumbnail-container img')):
            raise ParseError(f"Не найден обязательный атрибут: 'gallery'")
        urls: list[str] = [self._safe_extract_url(img, "data-src") for img in imgs]
        
        if urls:
            logger.debug(f"Обнаружено: {len(urls)} изображений")
            return urls
        
        raise ParseError("Не найден ни одна ссылка на изображение")
    
    def _extract_genres(self, soup):
        return self.extract_tags(soup).get("Теги", [])
    
    def _extract_author(self, soup):
        if author := self.extract_tags(soup).get("Автор"):
            return "".join(author)
        return None
        
    def _extract_language(self, soup):
        if language := self.extract_tags(soup).get("Автор"):
            return "".join(language)
        return None
    
    @lru_cache(1)
    def extract_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        objects = {}
        for tag in filter_truthy(soup.select(".tag-container.field-name")):
            if not tag.next_element:
                continue
            
            tag_name = tag.next_element.get_text(strip=True)
            tag_objects = [a.get_text(strip=True) for a in tag.select("a")]
            objects[tag_name] = tag_objects
        return objects