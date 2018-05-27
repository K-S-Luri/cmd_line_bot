import random, os, re
from .util import shuffle, get_cmd_line
from . import imgkit
import asyncio
from .error import DCError
from .config import config

from abc import ABC, abstractmethod

# メッセージ処理関数の本体
async def manage_msg(msg):
    global config
    global results
    cmd_line = get_cmd_line(msg)
    if cmd_line is None:
        return
    main_cmd = DCCmd_Main()
    await main_cmd.run(msg, args=cmd_line)

# コマンドのテンプレート
class DCCmd(ABC):
    def __init__(self):
        self._cmds = []
        self._documentation = "Not documented"
    def accept(self, cmd):
        return cmd in self._cmds
    def get_cmds(self):
        return self._cmds
    def get_usage(self):
        return "__%s__ %s\n" % (self.get_cmds(), self._documentation)

    @abstractmethod
    async def run(self, msg, args):
        pass

class DCCmdWithSub(DCCmd):
    def __init__(self):
        self._subcmds = []
    async def run(self, msg, args):
        error_msg = ""
        if len(args) == 0:
            error_msg += "[Error]サブコマンドを入力して下さい\n"
        else:
            cmd = args[0]
            for subcmd in self._subcmds:
                if subcmd.accept(cmd):
                    await subcmd.run(msg, args=args[1:])
                    return
            error_msg = "[Error] コマンド名が不正です\n"
        error_msg += "コマンド一覧:\n"
        for subcmd in self._subcmds:
            error_msg += subcmd.get_usage()
        await reply_to_msg(error_msg, msg)

class DCDebugCmd(DCCmd):
    def get_usage(self):
        orig_usage = super().get_usage()
        return "-" + orig_usage

# 全コマンドのroot
class DCCmd_Main(DCCmdWithSub):
    _documentation = "main"
    def __init__(self):
        self._subcmds = [DCCmd_Init(),
                         DCCmd_Example(),]

# 個々のコマンド
class DCCmd_Init(DCCmd):
    def __init__(self):
        self._cmds = ["init", "i"]
        self._documentation = "拠点となるサーバーを設定する．\nDMではなくサーバー内のテキストチャンネルで送る必要がある"
    async def run(self, msg, args):
        global config
        config.set_server(msg.server)
        config.set_channel(msg.channel)
        config.save_server_channel()
        text = "init OK\nサーバー情報を%sに保存しました．次回以降は__!init__は不要です" % config.get_user_config_file()
        await reply_to_msg(text, msg)

class DCCmd_Example(DCCmd):
    def __init__(self):
        self._cmds = ["example", "e"]
        self._documentation = "コマンドの例です"
    async def run(self, msg, args):
        global config
        text = "hgoeeee"
        await send_msg_to_channel(text=text)

# メッセージ送信用の関数たち
async def send_msg_to_channel(text):
    global config
    client = config.get_client()
    channel = config.get_channel()
    await client.send_message(channel, text)
async def reply_to_msg(text, msg):
    global config
    client = config.get_client()
    await client.send_message(msg.channel, text)

async def send_dm(text=None, filename=None, to=None):
    """'to'の値:
- ユーザー名(文字列) -> そのユーザーにDMを送る
- None -> players 全員にDMを送る"""
    global config
    if to is None:
        players = config.get_players()
        observers = config.get_observers()
        cors = []
        for p in players + observers:
            cors.append(send_dm_to_username(p, text, filename))
        await asyncio.gather(*cors)
    else:
        await send_dm_to_username(to, text, filename)

async def send_dm_to_username(username, text=None, filename=None):
    global config
    server = config.get_server()
    user = server.get_member_named(username)
    if user is None:
        raise DCError("ユーザー%sが見つかりません" % username)
    await send_dm_to_user(user, text=text, filename=filename)

async def send_dm_to_user(user, text=None, filename=None):
    global config
    client = config.get_client()
    if text is not None:
        await client.send_message(user, text)
    if filename is not None:
        await client.send_file(user, filename)
