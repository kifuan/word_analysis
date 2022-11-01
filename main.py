import argparse

from analysis import plot, parser_table, MessageParser, MessageCounter


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Word counter for QQ')
    parser.add_argument('-f', '--file', action='store', dest='file', required=True, help='The chat-history file.')
    parser.add_argument('-q', '--qid', action='store', dest='qid',
                        help='The QQ id you want to analyze. It should be QQ code when '
                             'mode is group, and name when mode is friend.')
    parser.add_argument('-l', '--limit', action='store', dest='limit', type=int, default=10, help='The limit of words.')
    parser.add_argument('-m', '--mode', action='store', dest='mode', default=parser_table.default_mode,
                        help='The parser mode.', choices=parser_table.keys())
    parser.add_argument('-w', '--words', action='store', dest='words', default='', help='If you only count for words '
                                                                                       'and find who said the most, '
                                                                                       'fill this, separated by comma.')
    return parser.parse_args()


def main():
    args = get_args()
    parser = MessageParser.get_parser(args.mode)
    counter = parser.parse_file(args.file)

    names: list[str]
    counts: list[int]
    label: str
    if args.words != '':
        names, counts = MessageCounter.get_topn(
            counter.count_for_words(args.words.split(',')), args.limit
        )
        names = [parser.get_display_name(n) for n in names]
        label = args.words
    else:
        names, counts = MessageCounter.get_topn(
            counter.count_for_person(args.qid), args.limit
        )
        label = parser.get_display_name(args.qid)

    actual_limit = min(args.limit, len(names))
    plot(f'{label}的词频 - Top{actual_limit}', names, counts)


if __name__ == '__main__':
    main()
