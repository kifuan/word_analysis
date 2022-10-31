import re
import sys
import jieba
import pkgutil
import collections
from abc import ABC, abstractmethod
from .parser import LineData, MessageParser

STOPWORDS = (
    pkgutil.get_data(__name__, 'stopwords.txt')
    .decode('utf-8')
    .splitlines()
)

NAME_LIMIT = 7

# Remove emojis, spaces, [xxx], @xxx.
REMOVE_MESSAGE_PATTERN = re.compile(r'[\U00010000-\U0010ffff]|\s|(\[.*?])|(@.+\s)')


def cut_messages(messages: list[str]) -> list[str]:
    words = []
    for msg in messages:
        msg = REMOVE_MESSAGE_PATTERN.sub('', msg)
        if msg == '':
            continue
        words.extend(word for word in jieba.cut(msg) if word not in STOPWORDS)
    return words


class Counter(ABC):
    @staticmethod
    def for_words(words: list[str], data: LineData, parser: MessageParser) -> 'Counter':
        return WordCounter(words, data, parser)

    @staticmethod
    def for_person(qid: str, data: LineData) -> 'Counter':
        if qid not in data.keys():
            raise KeyError(f'{qid} does not exist in the file. '
                           'Please ensure that you should find him/her by QQ ID or Email.')
        return PersonCounter(data[qid])

    @abstractmethod
    def count(self) -> dict[str, int]:
        raise NotImplementedError()


class PersonCounter(Counter):
    def __init__(self, messages: list[str]):
        self.messages = messages

    def count(self) -> dict[str, int]:
        return collections.Counter(cut_messages(self.messages))


class WordCounter(Counter):
    def __init__(self, words: list[str], data: LineData, parser: MessageParser):
        self.words = words
        self.data = data
        self.parser = parser

    def count(self) -> dict[str, int]:
        result = {}
        for qid, msgs in self.data.items():
            name = self.parser.get_display_name(qid)
            if name in result:
                print(f'There are two or more people named {name}, we will keep whose qid is {qid}', file=sys.stderr)
            msgs = cut_messages(msgs)
            result[name[:NAME_LIMIT]] = sum(msgs.count(word) for word in self.words)
        return result
