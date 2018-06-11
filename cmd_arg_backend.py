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
        cmdargline = CLBCmdArgLine(cmdline)
        cmdargline.parse(self._parser)
        if cmdargline.parsed_content is None:
            return []
        return self._rootcmd.run(cmdargline, -1)

# コマンドのテンプレート
class CLBCmd(metaclass=ABCMeta):
    def __init__(self):
        self._keys = []
        self._documentation = "Not documented"
    def accept_key(self, key):
        return key in self._keys
    def accept(self, cmdargline, pointer):
        return self.accept_key(cmdargline.get_key(pointer))
    def get_keys(self):
        return self._keys
    def get_usage(self):
        return "__%s__ %s\n" % (self.get_keys(), self._documentation)
    @abstractmethod
    def run(self, cmdargline, pointer):
        pass

class CLBCmdWithSub(CLBCmd):
    def __init__(self):
        self._subcmds = []
    def run(self, cmdargline, pointer):
        assert isinstance(cmdargline, CLBCmdArgLine), "%s is not a CLBCmdArgLine" % cmdargline
        assert cmdargline.get_num_args(pointer) >= 0
        error_msg = ""
        if cmdargline.get_num_args(pointer) <= 0:
            error_msg += "サブコマンドを入力して下さい\n"
        else:
            for subcmd in self._subcmds:
                if subcmd.accept(cmdargline, pointer+1):
                    return subcmd.run(cmdargline, pointer+1)
            error_msg = "サブコマンド名(%s)が不正です\n" % cmdargline.get_key(pointer+1)
        error_msg += "コマンド一覧:\n"
        for subcmd in self._subcmds:
            error_msg += subcmd.get_usage()
        raise CLBError(error_msg)

# API用のクラスを拡張
class CLBCmdArgLine:
    def __init__(self, cmdline):
        self._cmdline = cmdline
    def parse(self, parser):
        self.parsed_content = parser(self._cmdline.content)
        if self.parsed_content is None:
            return
        assert isinstance(self.parsed_content, list)
        assert len(self.parsed_content) > 0
    def get_key(self, pointer):
        if not hasattr(self, "parsed_content"):
            raise CLBError("先にparseして下さい")
        assert self.parsed_content is not None
        if pointer >= len(self.parsed_content):
            raise CLBIndexError("不正なindexです")
        return self.parsed_content[pointer]
    def get_num_args(self, pointer):
        return len(self.parsed_content) - pointer - 1
    def get_args(self, pointer):
        assert self.get_num_args(pointer) >= 0
        return self.parsed_content[pointer+1:]
