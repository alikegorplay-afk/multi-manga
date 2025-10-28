from typing import Iterable, TypeVar, Iterator

T = TypeVar('T')

def filter_truthy(iterable: Iterable[T | None]) -> Iterator[T]:
    """Фильтрует итерируемый объект, оставляя только truthy значения.
    
    Args:
        iterable: Итерируемый объект, который может содержать None или ложные значения
        
    Yields:
        Только те элементы, которые являются truthy (не None, не пустые, не False)
    """
    for item in iterable:
        if item:
            yield item