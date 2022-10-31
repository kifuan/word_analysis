import re
from abc import ABC, abstractmethod
from typing import Type

# A dict that contains qid with all words they sent.
WordData = dict[str, list[str]]


class ScanningError(Exception):
    ...


class ConcreateParserTable:
    def __init__(self):
        self.table = {}

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
    @abstractmethod
    def extract_id(self, line: str, line_number: int) -> str:
        ...

    @staticmethod
    def get_parser(name: str) -> 'MessageParser':
        return concreate_parser.get(name)

    def parse_file(self, path: str) -> WordData:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [line.strip('\n') for line in f if line.strip('\n') != '']
        result = {}
        # The state of scanning.
        scanning_state = False
        # The metadata it is scanning for.
        scanning_for = ''
        i = 0
        while i < len(lines):
            line_contains_id = starts_with_date(lines[i])
            if scanning_state:
                # End of scanning for this term.
                if line_contains_id:
                    # Note that we don't increment i there,
                    # so that next loop will enter is_metadata branch.
                    scanning_state = False
                    continue
                result[scanning_for].append(lines[i])
                # Scan for next message, skip this line.
                i += 1
            elif line_contains_id:
                scanning_state = True
                scanning_for = self.extract_id(lines[i], i)
                result.setdefault(scanning_for, [])
                # Scan for messages, skip this line.
                i += 1
            else:
                raise ScanningError(
                    f'This line is neither message nor metadata.'
                    f'Line number: {i + 1}\n'
                    f'Content: {lines[i]}'
                )

        return result


def starts_with_date(line: str):
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
