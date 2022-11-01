import matplotlib.pyplot as plt
from typing import Iterable
from .parser import MessageParser

# Support for Chinese characters.
plt.rcParams["font.sans-serif"] = ['Microsoft YaHei', 'Heiti']


def get_topn(counter: dict[str, int], limit: int) -> tuple[Iterable[str], Iterable[int]]:
    items = sorted(counter.items(), key=lambda item: item[1], reverse=True)[:limit]
    print(f'The data to show is {items}')
    if len(items) == 0:
        raise ValueError('cannot get any data')
    words, counts = zip(*items)
    return words, counts


def plot_for_person(*, file: str, mode: str, qid: str, limit: int):
    parser = MessageParser.get_parser(mode)
    counter = parser.parse_file(file)
    words, nums = get_topn(counter.count_for_person(qid), limit)
    plt.bar(words, nums)
    plt.title(f'{parser.get_display_name(qid)}的词频 - Top {min(len(list(nums)), limit)}')
    plt.show()


def plot_for_words(*, file: str, mode: str, words: list[str], limit: int):
    parser = MessageParser.get_parser(mode)
    counter = parser.parse_file(file)
    ids, nums = get_topn(counter.count_for_words(words), limit)
    plt.bar([parser.get_display_name(qid) for qid in ids], nums)
    plt.title(f'{",".join(words)}出现的频率 - Top {min(len(list(nums)), limit)}')
    plt.show()
