import json
import jieba
import collections
import re
import matplotlib.pyplot as plt
from typing import *


# Support for Chinese characters
plt.rcParams["font.sans-serif"] = ['Microsoft YaHei']


def load(json_path: str, qid: str) -> List[str]:
    with open(json_path, 'r', encoding='utf-8') as f:
        messages = json.load(f)[qid]

    # Remove emoji and spaces
    useless_pattern = re.compile(r'[\U00010000-\U0010ffff]|\s|(\[.*?])')
    messages_with_empty = [useless_pattern.sub('', msg) for msg in messages]
    return [msg for msg in messages_with_empty if msg != '']


def count_words(messages: List[str]) -> Dict[str, int]:
    words = []
    for message in messages:
        words.extend(jieba.cut(message))
    return collections.Counter(words)


def plot(json_path: str, qid: str, limit: int):
    counter = count_words(load(json_path, qid))
    # Sort the words by frequencies
    items = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:limit]
    words, nums = zip(*items)
    plt.bar(words, nums)
    plt.title(f'{qid}的词频 - Top{limit}')
    plt.show()
