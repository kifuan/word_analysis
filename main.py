import sys
import argparse
from analysis import plot, parser_table


def parse_args():
    parser = argparse.ArgumentParser(description='Word counter for QQ')
    parser.add_argument('-f', '--file', action='store', dest='file', required=True, help='The chat-history file.')
    parser.add_argument('-i', '--qid', action='store', dest='qid', required=True, help='The QQ id you want to analyze.')
    parser.add_argument('-l', '--limit', action='store', dest='limit', default=30, help='The limit of words.')
    parser.add_argument('-m', '--mode', action='store', dest='mode', default=parser_table.default_mode,
                        help='The parser mode.', choices=parser_table.keys())


if __name__ == '__main__':
    path, mode, qid, limit = sys.argv[1:]
    limit = int(limit)
    plot(path, mode, qid, limit)
