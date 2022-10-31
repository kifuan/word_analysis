import warnings
from typing import Type, TypeVar, Generic

T = TypeVar('T')


class ConcreateTable(Generic[T]):
    def __init__(self):
        self.table: dict[str, T] = {}
        self.default_mode = None

    def keys(self) -> list[str]:
        return list(self.table.keys())

    def get(self, mode: str) -> T:
        if mode not in self.table:
            raise KeyError(f'no parser mode {mode}')
        return self.table[mode]

    def register(self, mode: str, *, default: bool = False):
        if default:
            if self.default_mode is not None:
                warnings.warn(f'cannot set mode {mode} to default '
                              f'because {self.default_mode} is already set.')
            else:
                self.default_mode = mode

        if mode in self.table:
            warnings.warn(f'rewriting mode {mode}')

        def wrapper(t: Type[T]):
            self.table[mode] = t()
            return t

        return wrapper
