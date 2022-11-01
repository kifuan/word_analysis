import re
from abc import ABC, abstractmethod
from .concreate_table import ConcreateTable
from .message_counter import MessageCounter
from .state import State, StateSpecificMethod

ANGLE_BRACKETS_REGEX = re.compile(r'<(.*?)>')
BRACKETS_REGEX = re.compile(r'[(](.*?)[)]')
DATE_HEAD_REGEX = re.compile(r'^(\d{4}-\d{2}-\d{2}\s+\d\d?:\d{2}:\d{2}\s*)')


class ScanningError(Exception):
    ...


parser_table: ConcreateTable['MessageParser'] = ConcreateTable()


class MessageParser(ABC):
    state_specific = StateSpecificMethod()

    def __init__(self):
        """
        Note that if subclass overrides __init__ and it takes arguments,
        please rewrite setup_vars as well.
        """
        self.state = State.EMPTY
        self.counter = MessageCounter()
        self.line_number = 0
        self.lines = []

    def setup_vars(self):
        # Just calls the __init__ method to set up variables,
        # and the subclass should override this method to
        # initialize if its __init__ takes arguments.
        self.__init__()

    @abstractmethod
    def extract_qid(self, line: str, line_number: int) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_display_name(self, qid: str) -> str:
        raise NotImplementedError()

    @staticmethod
    def get_parser(mode: str) -> 'MessageParser':
        return parser_table.get(mode)

    @property
    def line(self) -> str:
        return self.lines[self.line_number]

    @state_specific.register(State.EMPTY)
    def _(self):
        if DATE_HEAD_REGEX.search(self.line):
            self.state = State.ID
            return

        # If the counter hasn't started yet, and current line isn't seem to contain qid.
        if not self.counter.is_started():
            self.line_number += 1
            return

        self.state = State.MESSAGE

    @state_specific.register(State.ID)
    def _(self):
        self.counter.change_qid(self.extract_qid(self.line, self.line_number))
        self.line_number += 1
        self.state = State.EMPTY

    @state_specific.register(State.MESSAGE)
    def _(self):
        self.counter.add_message(self.line)
        self.line_number += 1
        self.state = State.EMPTY

    def parse_lines(self, lines: list[str]) -> MessageCounter:
        self.setup_vars()
        self.lines = lines
        while self.line_number < len(lines):
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

    def extract_qid(self, line: str, line_number: int) -> str:
        # Try to find it with ().
        brackets = BRACKETS_REGEX.findall(line)
        if brackets:
            return self.update_display_name(brackets[-1], line)

        # Try to find it with <>.
        angel_brackets = ANGLE_BRACKETS_REGEX.findall(line)
        if angel_brackets:
            return self.update_display_name(angel_brackets[-1], line)

        raise ScanningError(
            f'Cannot find qid or email in line {line_number + 1}.\n'
            f'Content: {line}\n'
            'Did you forget to choose the mode to friend?'
        )

    def get_display_name(self, qid: str) -> str:
        return self.display_name[qid]


@parser_table.register('friend')
class FriendMessageParser(MessageParser):
    def extract_qid(self, line: str, line_number: int) -> str:
        return DATE_HEAD_REGEX.sub('', line)

    def get_display_name(self, qid: str) -> str:
        # The friend parser uses displaying name as id, so it just returns qid.
        return qid
