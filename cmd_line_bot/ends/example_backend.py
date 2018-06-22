#!/usr/bin/env python3
from datetime import datetime

from .cmd_arg_backend import CmdArgBackEnd, CLBCmd, CLBCmdWithSub, CLBCmdArgLine  # , create_reply_task
from ..core.clb_interface import CLBTask, CLBTask_Msg, CLBTask_DM, create_reply_task
from ..core.clb_error import CLBError


class RootCmd(CLBCmdWithSub):
    def __init__(self):
        self._documentation = "root command"
        self._subcmds = [Cmd_Msg(),
                         Cmd_Dm(),
                         Cmd_File(),
                         Cmd_Reply(),
                         Cmd_Time()]


class Cmd_Msg(CLBCmd):
    def __init__(self):
        self._keys = ["msg", "message", "m"]
        self._documentation = "メッセージを送信"

    def run(self, cmdargline, pointer):
        assert isinstance(cmdargline, CLBCmdArgLine)
        if cmdargline.get_num_args(pointer) < 2:
            raise CLBError("引数が足りません")
        elif cmdargline.get_num_args(pointer) > 2:
            raise CLBError("引数が多すぎます")
        name, text = cmdargline.get_args(pointer)
        tasks = []
        tasks.append(CLBTask_Msg(channelname=name, text=text, cmdline=cmdargline.cmdline))
        return tasks


class Cmd_Dm(CLBCmd):
    def __init__(self):
        self._keys = ["dm", "d"]
        self._documentation = "ダイレクトメッセージを送信"

    def run(self, cmdargline, pointer):
        assert isinstance(cmdargline, CLBCmdArgLine)
        if cmdargline.get_num_args(pointer) < 2:
            raise CLBError("引数が足りません")
        elif cmdargline.get_num_args(pointer) > 2:
            raise CLBError("引数が多すぎます")
        name, text = cmdargline.get_args(pointer)
        tasks = []
        tasks.append(CLBTask_DM(username=name, text=text, cmdline=cmdargline.cmdline))
        return tasks


class Cmd_File(CLBCmd):
    def __init__(self):
        self._keys = ["file", "f"]
        self._documentation = "画像ファイル付きのメッセージを送信"

    def run(self, cmdargline, pointer):
        assert isinstance(cmdargline, CLBCmdArgLine)
        if cmdargline.get_num_args(pointer) < 2:
            raise CLBError("引数が足りません")
        elif cmdargline.get_num_args(pointer) > 2:
            raise CLBError("引数が多すぎます")
        name, text = cmdargline.get_args(pointer)
        tasks = []
        tasks.append(CLBTask_Msg(channelname=name, text=text,
                                 filename="dice.png", cmdline=cmdargline.cmdline))
        return tasks


class Cmd_Reply(CLBCmd):
    def __init__(self):
        self._keys = ["reply", "re", "r"]
        self._documentation = "コマンド入力元と同じチャンネル(or DM)にメッセージを送信"

    def run(self, cmdargline, pointer):
        assert isinstance(cmdargline, CLBCmdArgLine)
        if cmdargline.get_num_args(pointer) != 1:
            raise CLBError("引数の個数が不正です")
        text = cmdargline.get_args(pointer)[0]
        tasks = []
        tasks.append(create_reply_task(cmdargline.cmdline, text=text))
        return tasks


class Cmd_Time(CLBCmd):
    def __init__(self):
        self._keys = ["time", "t"]
        self._documentation = "現在時刻を表示する"

    def run(self, cmdargline, pointer):
        text = datetime.now().strftime("%H:%M:%S")
        tasks = [create_reply_task(cmdargline.cmdline, text=text)]
        return tasks


example_backend = CmdArgBackEnd(rootcmd=RootCmd())
