import sys
import argparse
from analysis import plot, parser_table


def parse_args():
    parser = argparse.ArgumentParser(description='Word counter for QQ')
    parser.add_argument('-f', '--file', action='store', dest='file', required=True, help='The chat-history file.')
    parser.add_argument('-q', '--qid', action='store', dest='qid', required=True,
                        help='The QQ id you want to analyze. It should be QQ code when '
                             'mode is group, and name when mode is friend.')
    parser.add_argument('-l', '--limit', action='store', dest='limit', type=int, default=30, help='The limit of words.')
    parser.add_argument('-m', '--mode', action='store', dest='mode', default=parser_table.default_mode,
                        help='The parser mode.', choices=parser_table.keys())
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    plot(args.file, args.mode, args.qid, args.limit)
