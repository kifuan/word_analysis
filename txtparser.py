import json
import re
from typing import *


class ScanningError(Exception):
    ...


def parse_metadata(line: str, current_line: int) -> Tuple[bool, str]:
    # It starts with date
    if not re.search(r'^(\d{4}-\d{2}-\d{2}.+)', line):
        return False, ''

    # Try to find it with ()
    brackets = re.findall(r'[(](.*?)[)]', line)
    if brackets:
        return True, brackets[-1]

    # Try to find it with <>
    angel_brackets = re.findall(r'[<](.*?)[>]', line)
    if angel_brackets:
        return True, angel_brackets[-1]

    if current_line == 0:
        raise ScanningError('You should ensure that you removed BOM and extra lines auto-generated by QQ following '
                            'README.MD')

    raise ScanningError(f'Cannot find qid or email in line {current_line+1}, but this line starts with regular '
                        f'datetime, which is what we want.')


def scan_file(lines: List[str]) -> Dict[str, List[str]]:
    result = dict()
    # The state of scanning.
    scanning_state = False
    # The metadata it is scanning for.
    scanning_for = ''
    i = 0
    while i < len(lines):
        is_metadata, metadata = parse_metadata(lines[i], i)
        if scanning_state:
            # End of scanning for this term.
            if is_metadata:
                # Note that we don't increment i there,
                # so that next loop will enter is_metadata branch.
                scanning_state = False
                continue
            result[scanning_for].append(lines[i])
            # Scan for next message, skip this line.
            i += 1
        elif is_metadata:
            scanning_state = True
            scanning_for = metadata
            result.setdefault(metadata, [])
            # Scan for messages, skip this line.
            i += 1
        else:
            raise ScanningError(f'It is not scanning and this line is not metadata. Current line: {i+1}')

    return result


def parse(txt_path: str, json_path: str):
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = [line.strip('\n') for line in f if line.strip('\n') != '']
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(scan_file(lines), f, ensure_ascii=False)