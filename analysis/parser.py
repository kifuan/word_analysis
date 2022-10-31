import re
from typing import Type
from abc import ABC, abstractmethod
from .state import State, StateSpecificMethod


# A dict that contains qid with all words they sent.
LineData = dict[str, list[str]]


class ScanningError(Exception):
    ...


class ConcreateParserTable:
    def __init__(self):
        self.table: dict[str, 'MessageParser'] = {}

    def get(self, name: str) -> 'MessageParser':
        if name not in self.table:
            raise KeyError(f'no parser named {name}')
        return self.table[name]

    def register(self, name: str):
        def wrapper(t: Type['MessageParser']):
            self.table[name] = t()
            return t

        return wrapper


concreate_parser = ConcreateParserTable()


class MessageParser(ABC):
    state_specific = StateSpecificMethod()

    def __init__(self):
        self.state = State.EMPTY
        self.last_id = ''
        self.line_data: LineData = {}
        self.line_number = 0
        self.lines = []

    # Just make the code less strange, because we should initialize
    # properties before parsing, and calling __init__ is strange.
    setup_vars = __init__

    @abstractmethod
    def extract_id(self, line: str, line_number: int) -> str:
        raise NotImplementedError()

    @staticmethod
    def get_parser(name: str) -> 'MessageParser':
        return concreate_parser.get(name)

    @property
    def line(self) -> str:
        return self.lines[self.line_number]

    @state_specific.register(State.EMPTY)
    def _(self):
        if starts_with_date(self.line):
            self.state = State.ID
            return

        # It is the first line, but it does not contain id, so just skip it.
        if self.last_id == '':
            self.line_number += 1
            return

        self.state = State.MESSAGE

    @state_specific.register(State.ID)
    def _(self):
        assert starts_with_date(self.line), 'state ID should be applied when it starts with date.'
        self.last_id = self.extract_id(self.line, self.line_number)
        self.line_data.setdefault(self.last_id, [])
        self.state = State.MESSAGE
        self.line_number += 1
        self.state = State.EMPTY

    @state_specific.register(State.MESSAGE)
    def _(self):
        if starts_with_date(self.line):
            self.state = State.ID
            return
        self.line_data[self.last_id].append(self.line)
        self.line_number += 1
        self.state = State.EMPTY

    def parse_lines(self, lines: list[str]) -> LineData:
        self.setup_vars()
        self.lines = lines
        while self.line_number < len(lines):
            MessageParser.state_specific.apply(self.state, self)
        return self.line_data

    def parse_file(self, path: str) -> LineData:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [line.strip('\n') for line in f if line.strip('\n') != '']
        return self.parse_lines(lines)


def starts_with_date(line: str) -> bool:
    # It starts with date.
    return bool(re.search(r'^(\d{4}-\d{2}-\d{2}.+)', line))


@concreate_parser.register('group')
class GroupMessageParser(MessageParser):
    def extract_id(self, line: str, line_number: int) -> str:
        # Try to find it with ().
        brackets = re.findall(r'[(](.*?)[)]', line)
        if brackets:
            return brackets[-1]

        # Try to find it with <>.
        angel_brackets = re.findall(r'<(.*?)>', line)
        if angel_brackets:
            return angel_brackets[-1]

        raise ScanningError(
            f'Cannot find qid or email in line {line_number + 1}, but this line'
            'starts with regular datetime, which is what we want.'
        )


REMOVE_DATE = re.compile(r'^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s*)')


@concreate_parser.register('friend')
class FriendMessageParser(MessageParser):
    def extract_id(self, line: str, line_number: int) -> str:
        return REMOVE_DATE.sub('', line)
