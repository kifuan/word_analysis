import re
import jieba
import pkgutil
import collections
from .parser import LineData


STOPWORDS = (
    pkgutil.get_data(__name__, 'stopwords.txt')
    .decode('utf-8')
    .splitlines()
)


def preprocess_messages(messages: list[str]) -> list[str]:
    # Remove emojis, spaces, [xxx], @xxx.
    useless_pattern = re.compile(r'[\U00010000-\U0010ffff]|\s|(\[.*?])|(@.+\s)')
    messages_with_empty = [useless_pattern.sub('', msg) for msg in messages]
    return [msg for msg in messages_with_empty if msg != '']


def make_counter(data: LineData, qid: str) -> dict[str, int]:
    if qid not in data.keys():
        raise KeyError(f'{qid} does not exist in the file. '
                       'Please ensure that you should find him/her by QQ ID or Email.')

    messages = preprocess_messages(data[qid])
    words = []
    for message in messages:
        words.extend(word for word in jieba.cut(message) if word not in STOPWORDS)
    return collections.Counter(words)
