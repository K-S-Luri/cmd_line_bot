#!/usr/bin/env python3
from abc import ABCMeta, abstractmethod
from typing import Callable, List, Union, Optional, cast, Tuple

from ..core.cmd_line_bot import CLBBackEnd
from ..core.clb_interface import CLBCmdLine, CLBCmdLine_Msg, CLBTask
from ..core.clb_error import CLBError, CLBIndexError
from .parser import quote_parser


# API用のクラスを拡張
class CLBCmdArgLine:
    def __init__(self, cmdline: CLBCmdLine) -> None:
        self.cmdline = cmdline

    # def get_type(self) -> str:
    #     return self.cmdline.type

    def get_author(self) -> str:
        return self.cmdline.author

    def get_channelname(self) -> Optional[str]:
        cmdline = cast(CLBCmdLine_Msg, self.cmdline)
        return cmdline.channelname

    def parse(self,
              parser: Callable[[str], List[str]]) -> None:
        self.parsed_content = parser(self.cmdline.content)
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
        if pointer < 0:
            print("pointer(=%s)が負だけど大丈夫？" % pointer)
        return self.parsed_content[pointer]

    def get_num_args(self, pointer: int) -> int:
        return len(self.parsed_content) - pointer - 1

    def get_args(self, pointer: int) -> List[str]:
        assert self.get_num_args(pointer) >= 0
        return self.parsed_content[pointer + 1:]


# コマンドのテンプレート
class CLBCmd(metaclass=ABCMeta):
    def __init__(self) -> None:
        self._keys = []  # type: List[str]
        self._documentation = "Not documented"
        self._required_num_args = None  # type: Union[None, int, Tuple[int, Optional[int]]]

    def accept_key(self, key: str) -> bool:
        return key in self._keys

    def accept(self,
               cmdargline: CLBCmdArgLine,
               pointer: int) -> bool:
        return self.accept_key(cmdargline.get_key(pointer))

    def get_keys(self) -> List[str]:
        return self._keys

    def get_usage(self) -> str:
        keys = ", ".join(map(lambda key: "__`%s`__" % key,
                             self.get_keys()))
        keys = "[%s]" % keys
        return "%s %s\n" % (keys, self._documentation)

    def get_required_num_args(self) -> Tuple[int, Optional[int]]:
        if (not hasattr(self, "_required_num_args")) or (self._required_num_args is None):
            required_num_args = (0, None)  # type: Tuple[int, Optional[int]]
        elif isinstance(self._required_num_args, int):
            required_num_args = (self._required_num_args, self._required_num_args)
        elif isinstance(self._required_num_args, tuple):
            required_num_args = cast(Tuple[int, Optional[int]], self._required_num_args)
        else:
            raise CLBError("CLBCmd に設定された引数の情報が不正です")
        return required_num_args

    def has_valid_num_args(self,
                           cmdargline: CLBCmdArgLine,
                           pointer: int) -> bool:
        required_num_args = self.get_required_num_args()
        req_min, req_max = required_num_args
        given_num_args = cmdargline.get_num_args(pointer)
        if given_num_args < req_min:
            return False
        elif (req_max is not None) and (given_num_args > req_max):
            return False
        return True

    def get_str_valid_num_args(self) -> str:
        req_min, req_max = self.get_required_num_args()
        if req_max is None:
            req_max_str = "∞"
        else:
            req_max_str = str(req_max)
        return "[{req_min}, {req_max}]".format(req_min=req_min, req_max=req_max_str)

    def api_run(self,
                cmdargline: CLBCmdArgLine,
                pointer: int,
                send_task: Callable[[CLBTask], None]) -> None:
        # 関数名もうちょっと考えよう
        if not self.has_valid_num_args(cmdargline, pointer):
            error_msg = "{cmd}の引数の個数({num})が不正です\nRequired: {req}"
            error_msg = error_msg.format(cmd=cmdargline.get_key(pointer),
                                         num=cmdargline.get_num_args(pointer),
                                         req=self.get_str_valid_num_args())
            raise CLBError(error_msg)
        self.run(cmdargline, pointer, send_task)

    @abstractmethod
    def run(self,
            cmdargline: CLBCmdArgLine,
            pointer: int,
            send_task: Callable[[CLBTask], None]) -> None:
        pass


class CLBCmdWithSub(CLBCmd):
    def __init__(self) -> None:
        self._subcmds = []  # type: List[CLBCmd]

    def run(self,
            cmdargline: CLBCmdArgLine,
            pointer: int,
            send_task: Callable[[CLBTask], None]) -> None:
        assert isinstance(cmdargline, CLBCmdArgLine), "%s is not a CLBCmdArgLine" % cmdargline
        assert cmdargline.get_num_args(pointer) >= 0
        error_msg = ""
        if cmdargline.get_num_args(pointer) <= 0:
            error_msg += "サブコマンドを入力して下さい\n"
        else:
            for subcmd in self._subcmds:
                if subcmd.accept(cmdargline, pointer + 1):
                    subcmd.api_run(cmdargline, pointer + 1, send_task)
                    return
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

    def manage_cmdline(self,
                       cmdline: CLBCmdLine,
                       send_task: Callable[[CLBTask], None]) -> None:
        cmdargline = CLBCmdArgLine(cmdline)
        cmdargline.parse(self._parser)
        if len(cmdargline.parsed_content) == 0:
            return
        self._rootcmd.api_run(cmdargline, -1, send_task)

    def kill(self):
        pass
