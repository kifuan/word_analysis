import re
import jieba
import pkgutil
import collections
from typing import Generator, Any

# Remove emojis, spaces, [xxx], @xxx.
REMOVE_MESSAGE_PATTERN = re.compile(r'[\U00010000-\U0010ffff]|\s|(\[.*?])|(@.+\s)')

STOPWORDS = (
    pkgutil.get_data(__name__, 'stopwords.txt')
    .decode('utf-8')
    .splitlines()
)


def expand_generators(generators: list[Generator[str, Any, None]]) -> list[str]:
    return [item for gen in generators for item in gen]


class MessageCounter:
    def __init__(self):
        # We won't cut any message when building the counter,
        # because it will be expanded by function expand_generators when counting.
        self.data: dict[str, list[Generator[str, Any, None]]] = {}
        self.qid: str = ''

    def is_started(self) -> bool:
        return self.qid != ''

    def change_qid(self, qid: str):
        self.qid = qid
        self.data.setdefault(qid, [])

    def add_message(self, message: str):
        message = REMOVE_MESSAGE_PATTERN.sub('', message)
        if message == '':
            return
        self.data[self.qid].append(
            word for word in jieba.cut(message) if word not in STOPWORDS
        )

    def count_for_person(self, qid: str) -> dict[str, int]:
        return collections.Counter(expand_generators(self.data[qid]))

    def count_for_words(self, words: list[str]) -> dict[str, int]:
        result = {}
        for qid, qid_words in self.data.items():
            count = sum(expand_generators(qid_words).count(word) for word in words)
            if count == 0:
                continue
            result[qid] = count
        return result
