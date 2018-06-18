#!/usr/bin/env python3
from cmd_line_bot import CLBTask
from cmd_arg_backend import CmdArgBackEnd, CLBCmd, CLBCmdWithSub, CLBCmdArgLine, create_reply_task
from clb_error import CLBError


class RootCmd(CLBCmdWithSub):
    def __init__(self):
        self._documentation = "root command"
        self._subcmds = [Cmd_Msg(),
                         Cmd_Dm(),
                         Cmd_File(),
                         Cmd_Reply()]


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
        tasks.append(CLBTask(tasktype="msg", channelname=name, text=text))
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
        tasks.append(CLBTask(tasktype="dm", username=name, text=text))
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
        tasks.append(CLBTask(tasktype="msg", channelname=name, text=text, filename="dice.png"))
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
        tasks.append(create_reply_task(cmdargline, text=text))
        return tasks


example_backend = CmdArgBackEnd(rootcmd=RootCmd())
