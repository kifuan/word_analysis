from typing import Type, TypeVar, Generic


T = TypeVar('T')


class ConcreateTable(Generic[T]):
    def __init__(self):
        self.table: dict[str, T] = {}

    def get(self, name: str) -> T:
        if name not in self.table:
            raise KeyError(f'no parser named {name}')
        return self.table[name]

    def register(self, name: str):
        def wrapper(t: Type[T]):
            self.table[name] = t()
            return t

        return wrapper
