import sys
from txtparser import parse
from analysis import plot


def main(name: str, qid: str, limit: int = 30):
    parse(f'{name}.txt', f'{name}.json')
    plot(f'{name}.json', qid, limit)


if __name__ == '__main__':
    main(sys.argv[0], 'test')
