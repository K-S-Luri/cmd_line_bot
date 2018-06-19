#!/usr/bin/env python3
from abc import ABCMeta, abstractmethod
from typing import Callable, List, Union, Optional

from cmd_line_bot import CLBBackEnd, CLBTask
from clb_interface import CLBCmdLine
from clb_error import CLBError, CLBIndexError
from parser import quote_parser


# API用のクラスを拡張
class CLBCmdArgLine:
    def __init__(self, cmdline: CLBCmdLine) -> None:
        self._cmdline = cmdline

    def get_type(self) -> str:
        return self._cmdline.type

    def get_author(self) -> str:
        return self._cmdline.author

    def get_channelname(self) -> Optional[str]:
        return self._cmdline.channelname

    def parse(self,
              parser: Callable[[str], List[str]]) -> None:
        self.parsed_content = parser(self._cmdline.content)
        if len(self.parsed_content) == 0:
            return
        assert isinstance(self.parsed_content, list)
        assert len(self.parsed_content) > 0

    def get_key(self, pointer: int) -> str:
        if not hasattr(self, "parsed_content"):
            raise CLBError("先にparseして下さい")
        assert len(self.parsed_content) > 0
        if pointer >= len(self.parsed_content):
            raise CLBIndexError("不正なindexです")
        return self.parsed_content[pointer]

    def get_num_args(self, pointer: int) -> int:
        return len(self.parsed_content) - pointer - 1

    def get_args(self, pointer: int) -> List[str]:
        assert self.get_num_args(pointer) >= 0
        return self.parsed_content[pointer + 1:]


# コマンドのテンプレート
class CLBCmd(metaclass=ABCMeta):
    def __init__(self):
        self._keys = []
        self._documentation = "Not documented"

    def accept_key(self, key: str) -> bool:
        return key in self._keys

    def accept(self,
               cmdargline: CLBCmdArgLine,
               pointer: int) -> bool:
        return self.accept_key(cmdargline.get_key(pointer))

    def get_keys(self) -> List[str]:
        return self._keys

    def get_usage(self) -> str:
        return "__%s__ %s\n" % (self.get_keys(), self._documentation)

    @abstractmethod
    def run(self,
            cmdargline: CLBCmdArgLine,
            pointer: int) -> List[Union[CLBTask, List[CLBTask]]]:
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
                if subcmd.accept(cmdargline, pointer + 1):
                    return subcmd.run(cmdargline, pointer + 1)
            error_msg = "サブコマンド名(%s)が不正です\n" % cmdargline.get_key(pointer + 1)
        error_msg += "コマンド一覧:\n"
        for subcmd in self._subcmds:
            error_msg += subcmd.get_usage()
        raise CLBError(error_msg)


# (サブ)コマンドと引数からなるバックエンド
class CmdArgBackEnd(CLBBackEnd):
    def __init__(self,
                 rootcmd: CLBCmd,
                 parser: Callable[[str], List[str]] = quote_parser) -> None:
        self._parser = parser
        self._rootcmd = rootcmd

    def manage_cmdline(self, cmdline: CLBCmdLine) -> List[Union[CLBTask, List[CLBTask]]]:
        cmdargline = CLBCmdArgLine(cmdline)
        cmdargline.parse(self._parser)
        if len(cmdargline.parsed_content) == 0:
            return []
        return self._rootcmd.run(cmdargline, -1)


# utilities
def create_reply_task(cmdargline: CLBCmdArgLine,
                      text: Optional[str] = None,
                      filename: Optional[str] = None) -> CLBTask:
    tasktype = cmdargline.get_type()
    if tasktype == "msg":
        channelname = cmdargline.get_channelname()
        task = CLBTask(tasktype=tasktype, channelname=channelname, text=text, filename=filename)
    elif tasktype == "dm":
        author = cmdargline.get_author()
        task = CLBTask(tasktype=tasktype, username=author, text=text, filename=filename)
    else:
        raise CLBError("Invalid tasktype")
    return task
