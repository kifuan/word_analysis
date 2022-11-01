from typing import TypeVar, Generic

T = TypeVar('T')


class ListReader(Generic[T]):
    def __init__(self, lst: list[T]):
        self.lst = lst
        self.i = 0

    @property
    def cur(self) -> T:
        return self.lst[self.i]

    def get_cur_and_next(self) -> T:
        data = self.cur
        self.i += 1
        return data

    def has_next(self) -> bool:
        return self.i < len(self.lst)
