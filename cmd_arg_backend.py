#!/usr/bin/env python3
from abc import ABCMeta, abstractmethod
from cmd_line_bot import CLBBackEnd, CLBTask, CLBCmdLine
from clb_error import CLBError, CLBIndexError

def space_sep_parser(cmdline_content):
    """`!cmd arg1 arg2`
    !で始まり，スペース区切り．
    そのうちquotationとかにも対応したい
    """
    if not cmdline_content.startswith("!"):
        return None
    parsed = cmdline_content[1:].split()
    if len(parsed) == 0:
        parsed = [""]
    return parsed

class CmdArgBackEnd(CLBBackEnd):
    def __init__(self, rootcmd, parser=space_sep_parser):
        self._parser = parser
        self._rootcmd = rootcmd
    def manage_cmdline(self, cmdline):
        assert isinstance(cmdline, CLBCmdLine)
        cmdline.parse(self._parser)
        if cmdline.parsed_content is None:
            return []
        return self._rootcmd.run(cmdline, -1)

# コマンドのテンプレート
class CLBCmd(metaclass=ABCMeta):
    def __init__(self):
        self._keys = []
        self._documentation = "Not documented"
    def accept_key(self, key):
        return key in self._keys
    def accept(self, cmdline, pointer):
        return self.accept_key(cmdline.get_nth_content(pointer))
    def get_keys(self):
        return self._keys
    def get_usage(self):
        return "__%s__ %s\n" % (self.get_keys(), self._documentation)
    @abstractmethod
    def run(self, cmdline, pointer):
        pass

class CLBCmdWithSub(CLBCmd):
    def __init__(self):
        self._subcmds = []
    def run(self, cmdline, pointer):
        assert cmdline.get_num_args(pointer) >= 0
        error_msg = ""
        if cmdline.len_parsed_content() <= pointer+1:
            error_msg += "サブコマンドを入力して下さい\n"
        else:
            for subcmd in self._subcmds:
                if subcmd.accept(cmdline, pointer+1):
                    return subcmd.run(cmdline, pointer+1)
            error_msg = "サブコマンド名(%s)が不正です\n" % cmdline.get_nth_content(pointer+1)
        error_msg += "コマンド一覧:\n"
        for subcmd in self._subcmds:
            error_msg += subcmd.get_usage()
        raise CLBError(error_msg)
