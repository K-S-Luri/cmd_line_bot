#!/usr/bin/env python3
from typing import List, Optional, Union

from ..core.clb_error import CLBError


def simple_parser(cmdline_content: str) -> List[str]:
    """`!cmd arg1 arg2`
    !で始まり，スペース区切り．
    """
    if not cmdline_content.startswith("!"):
        return []
    parsed = cmdline_content[1:].split()
    if len(parsed) == 0:
        parsed = [""]
    return parsed


def quote_parser(cmdline_content: str) -> List[str]:
    """`!cmd arg1 'arg2 with space'
    !で始まり，スペース区切り．quoteもできる
    """
    if not cmdline_content.startswith("!"):
        return []
    parsed = Parser(cmdline_content[1:]).get_parsed()
    if len(parsed) == 0:
        parsed = [""]
    return parsed


class Parser:
    sep_char = " "
    quote_chars = ["'", '"']
    escape_char = "\\"          # discord のエスケープ機能と衝突して上手くいかないかも？

    def __init__(self, text: str) -> None:
        self.text = text
        self.parsed = []  # type: List[str]
        self.current = ""
        self.pointer = 0
        self.escaped = False
        self.quoted = False  # type: Union[bool, str]

    def read(self) -> bool:
        if self.pointer == len(self.text):
            if self.quoted:
                raise CLBError("quotationが閉じられていません")
            if self.current != "":
                self.parsed.append(self.current)
            return False
        char = self.text[self.pointer]
        if self.quoted:
            if self.escaped:
                self.current += char
                self.escaped = False
                return True
            if char == self.quoted:
                self.parsed.append(self.current)
                self.current = ""
                self.quoted = False
                return True
            if char == self.escape_char:
                self.escaped = True
                return True
            self.current += char
            return True
        if char == self.sep_char:
            if self.current == "":
                return True
            else:
                self.parsed.append(self.current)
                self.current = ""
                return True
        if (self.current == "") and (char in self.quote_chars):
            self.quoted = char
            return True
        self.current += char
        return True

    def get_parsed(self) -> List[str]:
        self.parsed = []
        self.current = ""
        self.pointer = 0
        self.escaped = False
        self.quoted = False
        while True:
            # print(self.text[self.pointer])
            success = self.read()
            if not success:
                break
            self.pointer += 1
        return self.parsed


if __name__ == '__main__':
    text = r""" hoge 'fu"\'ga'a "pi\yo\\ foo" bar"""
    p = Parser(text)
    for s in p.get_parsed():
        print(s)
