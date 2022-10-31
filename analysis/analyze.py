import sys
import jieba
import collections
import re
import matplotlib.pyplot as plt

from typing import Iterable

from .parser import MessageParser, WordData


# Read stopwords.
with open('../stopwords.txt', 'r', encoding='utf-8') as stopwords_f:
    STOPWORDS = {word.strip('\n') for word in stopwords_f}


def preprocess_messages(messages: list[str]) -> list[str]:
    # Remove emojis, spaces, [xxx], @xxx.
    useless_pattern = re.compile(r'[\U00010000-\U0010ffff]|\s|(\[.*?])|(@.+\s)')
    messages_with_empty = [useless_pattern.sub('', msg) for msg in messages]
    return [msg for msg in messages_with_empty if msg != '']


def make_words_counter(messages: list[str]) -> dict[str, int]:
    words = []
    for message in messages:
        words.extend(set(jieba.cut(message)) - STOPWORDS)
    return collections.Counter(words)


def count(data: WordData, qid: str, limit: int) -> tuple[Iterable[str], Iterable[int]]:
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


def main():
    name, qid, limit = sys.argv[1:]
    limit = int(limit)
    data = MessageParser.get_parser('group').parse_file(f'{name}.txt')
    words, nums = count(data, qid, limit)
    plt.bar(words, nums)
    plt.title(f'{qid}的词频 - Top{limit}')
    plt.show()
