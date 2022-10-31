from enum import Enum


class State(Enum):
    EMPTY = 1
    ID = 2
    MESSAGE = 3


class StateSpecificMethod:
    table: dict[State, callable] = {}

    def register(self, state: State):
        def wrapper(f):
            self.table[state] = f
            return f

        return wrapper

    def apply(self, state: State, *args, **kwargs):
        self.table[state](*args, **kwargs)
