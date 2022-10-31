import re
from abc import ABC, abstractmethod
from typing import Literal


# A dict that contains qid with all words they sent.
WordData = dict[str, list[str]]


class ScanningError(Exception):
    ...


class MessageParser(ABC):
    @abstractmethod
    def _parse_metadata(self, line: str, line_number: int) -> tuple[bool, str]:
        ...

    @staticmethod
    def get_parser(kind: Literal["group"]) -> 'MessageParser':
        if kind == 'group':
            return GroupMessageParser()

    def parse_file(self, path: str) -> WordData:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [line.strip('\n') for line in f if line.strip('\n') != '']
        result = dict()
        # The state of scanning.
        scanning_state = False
        # The metadata it is scanning for.
        scanning_for = ''
        i = 0
        while i < len(lines):
            is_metadata, metadata = self._parse_metadata(lines[i], i)
            if scanning_state:
                # End of scanning for this term.
                if is_metadata:
                    # Note that we don't increment i there,
                    # so that next loop will enter is_metadata branch.
                    scanning_state = False
                    continue
                result[scanning_for].append(lines[i])
                # Scan for next message, skip this line.
                i += 1
            elif is_metadata:
                scanning_state = True
                scanning_for = metadata
                result.setdefault(metadata, [])
                # Scan for messages, skip this line.
                i += 1
            else:
                raise ScanningError(
                    f'This line is neither message nor metadata.'
                    f'Line number: {i + 1}\n'
                    f'Content: {lines[i]}'
                )

        return result


class GroupMessageParser(MessageParser):
    def _parse_metadata(self, line: str, line_number: int) -> tuple[bool, str]:
        # It starts with date.
        if not re.search(r'^(\d{4}-\d{2}-\d{2}.+)', line):
            if line_number == 0:
                raise ScanningError(
                    'You should ensure that you removed BOM and'
                    'extra lines auto-generated by QQ following README.MD'
                )
            # Just ignore the line if it is not the first.
            return False, ''

        # Try to find it with ().
        brackets = re.findall(r'[(](.*?)[)]', line)
        if brackets:
            return True, brackets[-1]

        # Try to find it with <>.
        angel_brackets = re.findall(r'[<](.*?)[>]', line)
        if angel_brackets:
            return True, angel_brackets[-1]

        raise ScanningError(
            f'Cannot find qid or email in line {line_number + 1}, but this line'
            'starts with regular datetime, which is what we want.'
        )