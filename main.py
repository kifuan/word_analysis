import sys
import argparse

from analysis import Plotter, parser_table


def get_plotter_from_args() -> Plotter:
    parser = argparse.ArgumentParser(description='Word counter for QQ')
    parser.add_argument('-f', '--file', action='store', dest='file', required=True, help='The chat-history file.')
    parser.add_argument('-q', '--qid', action='store', dest='qid',
                        help='The QQ id you want to analyze. It should be QQ code when '
                             'mode is group, and name when mode is friend.')
    parser.add_argument('-l', '--limit', action='store', dest='limit', type=int, default=10, help='The limit of words.')
    parser.add_argument('-m', '--mode', action='store', dest='mode', default=parser_table.default_mode,
                        help='The parser mode.', choices=parser_table.keys())
    parser.add_argument('-w', '--words', action='store', dest='word', default='', help='If you only count for words '
                                                                                       'and find who said the most, '
                                                                                       'fill this, separated by comma.')
    args = parser.parse_args()

    # Plot for words.
    if args.word != '':
        return Plotter.for_words(
            file=args.file,
            mode=args.mode,
            words=args.word.split(','),
            limit=args.limit
        )

    # Plot for person.
    if args.qid == '':
        raise KeyError('you must specify qid')

    return Plotter.for_person(
        file=args.file,
        mode=args.mode,
        qid=args.qid,
        limit=args.limit
    )


if __name__ == '__main__':
    get_plotter_from_args().plot()
