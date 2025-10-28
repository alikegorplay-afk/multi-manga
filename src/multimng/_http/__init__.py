from typing import Protocol, overload
from urllib.parse import urljoin
from inspect import iscoroutinefunction as is_async

from .errors import HTTPError

class Response(Protocol):
    content: bytes
    text: str
    
    status_code: int
    status: int
    
    data: bytes
    
    def raise_for_status(self) -> None: ...
    
    def read(self) -> bytes: ...
    
    def text(self) -> str: ...

class HasRequest(Protocol):
    @overload
    def request(*args, **kwargs) -> Response: ...
    
    @overload
    async def request(*args, **kwargs) -> Response: ...
    
class URL(Protocol): ...

class BaseHttpManager:
    def __init__(
        self,
        session: HasRequest
    ):
        if isinstance(session, BaseHttpManager):
            self._session = session._session
        elif hasattr(session, 'request'):
            self._session = session
        else:
            raise TypeError(f"Неподдерживаемый тип: {type(session).__name__}")
    
    def raise_for_response(self, response: Response):
        if hasattr(response, 'raise_for_status'):
            response.raise_for_status()
            return 
        
        elif hasattr(response, 'status_code'):
            status: int = response.status_code
            
        elif hasattr(response, 'status'):
            status: int = response.status
        
        else:
            raise AttributeError(f"Неподдерживаемый тип: {type(response).__name__}")

        if 200 <= status < 300:
            return
        
        raise HTTPError(f"Неожиданный код ответа: {status}")
    
    def _sync_get(self, url: str | URL, headers: dict[str, str] = {'referer': 'https://anihidecq.org/'}) -> str:
        response = self._session.request(method = "GET", url = url, headers = headers)
        
        self.raise_for_response(response)
        try:
            return response.text
        except AttributeError:
            return response.data.decode()
    
    def _sync_get_content(self, url: str | URL, headers: dict[str, str] = {'referer': 'https://anihidecq.org/'}) -> bytes:
        response = self._session.request(method = "GET", url = url, headers = headers)
            
        self.raise_for_response(response)
        try:
            return response.content
        except AttributeError:
            try:
                return response.data
            except AttributeError:
                return response.read()
    
    async def _async_get(self, url: str | URL, headers: dict[str, str] = {'referer': 'https://anihidecq.org/'}) -> str:
        if is_async(self._session.request):
            ...
        elif is_async(self._session.request):
            ...
        else:
            raise TypeError("Данный класс не поддерживает асинхронность")
        is_httpx = hasattr(self._session, '__class__') and 'httpx' in str(self._session.__class__)
        try:
            if is_httpx:
                raise TypeError()
            async with self._session.request(method="GET", url=url, headers=headers) as response:
                self.raise_for_response(response)
                return await response.text()
            
        except (AttributeError, TypeError):
            response = await self._session.request(method="GET", url=url, headers=headers)
            self.raise_for_response(response)
            return response.text
        
    async def _async_get_content(self, url: str | URL, headers: dict[str, str] = {'referer': 'https://anihidecq.org/'}) -> bytes:
        if hasattr(self._session, "__aenter__"):
            ...
        elif is_async(self._session.request):
            ...
        else:
            raise TypeError("Данный класс не поддерживает асинхронность")
        
        is_httpx = hasattr(self._session, '__class__') and 'httpx' in str(self._session.__class__)
        try:
            if is_httpx:
                raise TypeError()
            async with self._session.request(method="GET", url=url, headers=headers) as response:
                response.raise_for_status()
                return await response.read()
            
        except (AttributeError, TypeError):
            response = await self._session.request(method="GET", url=url, headers=headers)
            response.raise_for_status()
            try:
                return response.content
            except AttributeError:
                return await response.read()