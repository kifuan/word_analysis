import re
from abc import ABC, abstractmethod
from .concreate_table import ConcreateTable
from .message_counter import MessageCounter
from .state import State, StateSpecificMethod
from .list_reader import ListReader

ANGLE_BRACKETS_REGEX = re.compile(r'<(.*?)>')
BRACKETS_REGEX = re.compile(r'[(](.*?)[)]')
DATE_HEAD_REGEX = re.compile(r'^(\d{4}-\d{2}-\d{2}\s+\d\d?:\d{2}:\d{2}\s*)')


class ScanningError(Exception):
    ...


parser_table: ConcreateTable['MessageParser'] = ConcreateTable()


# noinspection PyTypeChecker
class MessageParser(ABC):
    state_specific = StateSpecificMethod()

    def __init__(self):
        """
        Note that if subclass overrides __init__ and it takes arguments,
        please rewrite setup_vars as well.
        """
        self.state = State.EMPTY
        self.counter = MessageCounter()
        # We will initialize it in setup_vars.
        self.reader: ListReader[str] = None

    def setup_vars(self, reader: ListReader[str]):
        # Just calls the __init__ method to set up variables,
        # and the subclass should override this method to
        # initialize if its __init__ takes arguments.
        self.__init__()
        self.reader = reader

    @abstractmethod
    def extract_qid(self, line: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_display_name(self, qid: str) -> str:
        raise NotImplementedError()

    @staticmethod
    def get_parser(mode: str) -> 'MessageParser':
        return parser_table.get(mode)

    @state_specific.register(State.EMPTY)
    def _(self):
        if DATE_HEAD_REGEX.search(self.reader.cur):
            self.state = State.ID
            return

        # If the counter hasn't started yet, and current line isn't seem to contain qid.
        if not self.counter.is_started():
            self.reader.get_cur_and_next()
            return

        self.state = State.MESSAGE

    @state_specific.register(State.ID)
    def _(self):
        self.counter.change_qid(self.extract_qid(self.reader.get_cur_and_next()))
        self.state = State.EMPTY

    @state_specific.register(State.MESSAGE)
    def _(self):
        self.counter.add_message(self.reader.get_cur_and_next())
        self.state = State.EMPTY

    def parse_lines(self, lines: list[str]) -> MessageCounter:
        self.setup_vars(ListReader(lines))
        while self.reader.has_next():
            MessageParser.state_specific.apply(self.state, self)
        return self.counter

    def parse_file(self, path: str) -> MessageCounter:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [line.strip('\n ') for line in f if not line.isspace()]
        return self.parse_lines(lines)


@parser_table.register('group', default=True)
class GroupMessageParser(MessageParser):
    def __init__(self):
        super().__init__()
        self.display_name = {}

    # noinspection GrazieInspection
    def update_display_name(self, qid: str, line: str) -> str:
        """
        Updates the display name dictionary and returns qid.
        :param qid: the qid.
        :param line: the line.
        :return: the qid.
        """
        # 2 bracket characters should be removed as well.
        self.display_name[qid] = DATE_HEAD_REGEX.sub('', line[:-len(qid)-2]).strip()
        return qid

    def extract_qid(self, line: str) -> str:
        # Try to find it with ().
        brackets = BRACKETS_REGEX.findall(line)
        if brackets:
            return self.update_display_name(brackets[-1], line)

        # Try to find it with <>.
        angel_brackets = ANGLE_BRACKETS_REGEX.findall(line)
        if angel_brackets:
            return self.update_display_name(angel_brackets[-1], line)

        raise ScanningError(
            f'Cannot find qid or email in line {line}\n'
            'Did you forget to choose the mode to friend?'
        )

    def get_display_name(self, qid: str) -> str:
        return self.display_name[qid]


@parser_table.register('friend')
class FriendMessageParser(MessageParser):
    def extract_qid(self, line: str) -> str:
        return DATE_HEAD_REGEX.sub('', line)

    def get_display_name(self, qid: str) -> str:
        # The friend parser uses displaying name as id, so it just returns qid.
        return qid
