import re
import jieba
import pkgutil
import collections
import matplotlib.pyplot as plt
from typing import Iterable

from .parser import MessageParser, LineData

STOPWORDS = set(
    pkgutil.get_data(__name__, 'stopwords.txt')
    .decode('utf-8')
    .splitlines()
)


def preprocess_messages(messages: list[str]) -> list[str]:
    # Remove emojis, spaces, [xxx], @xxx.
    useless_pattern = re.compile(r'[\U00010000-\U0010ffff]|\s|(\[.*?])|(@.+\s)')
    messages_with_empty = [useless_pattern.sub('', msg) for msg in messages]
    return [msg for msg in messages_with_empty if msg != '']


def remove_stopwords(it: Iterable[str]) -> list[str]:
    return [item for item in it if item not in STOPWORDS]


def make_words_counter(messages: list[str]) -> dict[str, int]:
    words = []
    for message in messages:
        words.extend(remove_stopwords(jieba.cut(message)))
    return collections.Counter(words)


def count(data: LineData, qid: str, limit: int) -> tuple[Iterable[str], Iterable[int]]:
    if qid not in data.keys():
        raise KeyError(f'{qid} does not exist in the file. '
                       'Please ensure that you should find him/her by QQ ID or Email.')

    messages = preprocess_messages(data[qid])
    counter = make_words_counter(messages)
    # Sort the words by counts.
    items = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:limit]
    words, nums = zip(*items)
    return words, nums


# Support for Chinese characters.
plt.rcParams["font.sans-serif"] = ['Microsoft YaHei', 'Heiti']


def main(path: str, mode: str, qid: str, limit: int):
    limit = int(limit)
    parser = MessageParser.get_parser(mode)
    data = parser.parse_file(path)
    words, nums = count(data, qid, limit)
    plt.bar(words, nums)
    plt.title(f'{parser.get_display_name(qid)}的词频 - Top{limit}')
    plt.show()
