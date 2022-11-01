import warnings

import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from typing import Union

from .message_counter import MessageCounter
from .parser import MessageParser

# Support for Chinese characters.
plt.rcParams["font.sans-serif"] = ['Microsoft YaHei', 'Heiti']


def get_topn(counter: dict[str, int], limit: int) -> tuple[list[str], list[int]]:
    items = sorted(counter.items(), key=lambda item: item[1], reverse=True)[:limit]
    print(f'The data to show is {items}')
    if len(items) == 0:
        raise ValueError('cannot get any data')
    words, counts = map(list, zip(*items))
    return words, counts


class Plotter(ABC):
    def __init__(self, parser: MessageParser, file: str, qid_or_words: Union[str, list[str]], limit: int):
        self.parser = parser
        self.file = file
        self.qid_or_words = qid_or_words
        self.limit = limit

    @staticmethod
    def for_person(*, mode: str, file: str, qid: str, limit: int) -> 'Plotter':
        return PersonPlotter(MessageParser.get_parser(mode), file, qid, limit)

    @staticmethod
    def for_words(*, mode: str, file: str, words: list[str], limit: int) -> 'Plotter':
        return WordPlotter(MessageParser.get_parser(mode), file, words, limit)

    @abstractmethod
    def count(self, counter: MessageCounter) -> dict[str, int]:
        raise NotImplementedError()

    @abstractmethod
    def process_x_axis(self, x: list[str]) -> list[str]:
        raise NotImplementedError()

    @abstractmethod
    def get_title(self, actual_limit: int) -> str:
        raise NotImplementedError()

    def plot(self):
        counter = self.parser.parse_file(self.file)
        x, y = get_topn(self.count(counter), self.limit)
        plt.bar(self.process_x_axis(x), y)
        plt.title(self.get_title(min(len(y), self.limit)))
        plt.show()


class PersonPlotter(Plotter):
    def get_title(self, actual_limit: int) -> str:
        return f'{self.parser.get_display_name(self.qid_or_words)} - Top {actual_limit}'

    def process_x_axis(self, x: list[str]) -> list[str]:
        return x

    def count(self, counter: MessageCounter) -> dict[str, int]:
        assert isinstance(self.qid_or_words, str), 'qid must be string.'
        return counter.count_for_person(self.qid_or_words)


class WordPlotter(Plotter):
    def post_init(self):
        if isinstance(self.qid_or_words, str):
            self.qid_or_words = [self.qid_or_words]

    def get_title(self, actual_limit: int) -> str:
        return f'{",".join(self.qid_or_words)}出现频率 - Top {actual_limit}'

    def process_x_axis(self, x: list[str]) -> list[str]:
        return [self.parser.get_display_name(qid) for qid in x]

    def count(self, counter: MessageCounter) -> dict[str, int]:
        assert isinstance(self.qid_or_words, list), 'words must be list.'
        return counter.count_for_words(self.qid_or_words)
