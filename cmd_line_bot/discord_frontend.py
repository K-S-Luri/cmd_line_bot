#!/usr/bin/env python3
from typing import cast, Optional, Callable, Any, List
from pytypes import typechecked
import asyncio
from threading import Thread
from time import sleep

import discord
from .cmd_line_bot import CLBInputFrontEnd, CLBOutputFrontEnd
from .clb_interface import (CLBCmdLine, CLBCmdLine_Msg, CLBCmdLine_DM,
                            CLBTask, CLBTask_Msg, CLBTask_DM)
from .clb_error import CLBError
from .clb_data import CLBData


class DiscordConfig:
    def __init__(self,
                 client: discord.Client,
                 data: CLBData,
                 data_category: str) -> None:
        self.client = client
        self.data = data
        self.data_category = data_category
        self.data.add_category(data_category)
        self.server = None  # type: Optional[discord.Server]
        self._trying_login = False

    @typechecked
    def get_token(self) -> str:
        token = self.data.get(self.data_category, "token")
        if token is None:
            raise CLBError("設定ファイル(%s)でtokenを指定してください" % self.data.path)
        return cast(str, token)

    def get_server(self) -> discord.Server:
        if self.server is None:
            servername = cast(str, self.data.get(self.data_category, "servername"))
            self.set_server_named(servername)
        return cast(discord.Server, self.server)

    def set_server(self, server: discord.Server) -> None:
        self.server = server
        self.data.set(self.data_category, "servername", server.name)

    @typechecked
    def set_server_named(self, servername: str) -> bool:
        servers = self.client.servers
        for server in servers:
            if servername == server.name:
                self.set_server(server)
                return True
        return False

    async def reply_to_msg(self,
                           text: str,
                           msg: discord.Message) -> None:
        await self.client.send_message(msg.channel, text)

    def get_channel_named(self, channelname: str) -> Optional[discord.Channel]:
        server = self.get_server()
        if server is None:
            return None
        channels = server.channels
        for channel in channels:
            if channelname == channel.name:
                return channel
        return None

    def get_user_named(self, username: str) -> Optional[discord.User]:
        server = self.get_server()
        if server is None:
            return None
        return server.get_member_named(username)

    def save(self):
        self.data.save()

    async def on_ready(self) -> None:
        client = self.client
        print("logged in as")
        print("[name] %s" % client.user.name)
        print("[ id ] %s" % client.user.id)
        print("------")

    def run_client(self) -> None:
        client = self.client
        if client.is_logged_in:
            return
        if self._trying_login:
            asyncio.run_coroutine_threadsafe(client.wait_until_ready(),
                                             client.loop).result()
            return
        self._trying_login = True
        client.event(self.on_ready)  # clientログイン成功時の処理
        token = self.get_token()
        thread = Thread(target=client.run, args=(token,))
        thread.start()
        asyncio.run_coroutine_threadsafe(client.wait_until_ready(),
                                         client.loop).result()
        self._trying_login = False
        return

    def get_channelnames(self) -> List[str]:
        if self.server is None:
            return []
        server = cast(discord.Server, self.server)
        channels = server.channels
        return list(map(lambda c: c.name,
                        filter(lambda c: c.type == discord.ChannelType.text,
                               channels)))

    def get_usernames(self) -> List[str]:
        if self.server is None:
            return []
        server = cast(discord.Server, self.server)
        users = server.members
        return list(map(lambda u: u.name,
                        users))


# frontend
class DiscordInputFrontEnd(CLBInputFrontEnd):
    def __init__(self,
                 config: DiscordConfig,
                 init_cmd: str = "!init") -> None:
        self.config = config
        self.init_cmd = init_cmd

    async def on_message(self,
                         callback: Callable[[CLBCmdLine], None],
                         msg: discord.Message) -> None:
        if msg.content == self.init_cmd:
            await self.init_client(msg)
        if isinstance(msg.channel, discord.Channel):
            channelname = msg.channel.name
            cmdline = CLBCmdLine_Msg(content=msg.content,
                                     author=msg.author.name,
                                     channelname=channelname)
        elif isinstance(msg.channel, discord.PrivateChannel):
            cmdline = CLBCmdLine_DM(content=msg.content,
                                    author=msg.author.name)
        callback(cmdline)

    def run(self,
            callback: Callable[[CLBCmdLine], None]) -> None:
        client = self.config.client

        @client.event
        async def on_message(msg):
            await self.on_message(callback, msg)
        self.config.run_client()

    async def init_client(self,
                          msg: discord.Message) -> Any:  # 本当は返り値はCoroutineだけど，python3.5では未実装
        if msg.server is None:
            raise CLBError("`%s`は(DMではなく，サーバー内の)テキストチャンネルに送信してください" % self.init_cmd)
        print("[Initialize client]\nServer: %s" % msg.server)
        self.config.set_server(msg.server)
        self.config.save()
        await self.config.reply_to_msg("initしました", msg)

    def kill(self) -> None:
        client = self.config.client
        if client.is_logged_in:
            asyncio.run_coroutine_threadsafe(client.logout(), client.loop)


class DiscordOutputFrontEnd(CLBOutputFrontEnd):
    def __init__(self,
                 config: DiscordConfig) -> None:
        self.config = config

    def send_msg(self,
                 channelname: str,
                 text: Optional[str],
                 filename: Optional[str] = None) -> None:
        self.config.run_client()
        coro = self._send_msg(channelname=channelname, text=text, filename=filename)
        loop = self.config.client.loop
        asyncio.run_coroutine_threadsafe(coro, loop).result()  # .result()をつけて，完了するまで待っている

    def send_dm(self,
                username: str,
                text: Optional[str],
                filename: Optional[str] = None) -> None:
        self.config.run_client()
        coro = self._send_dm(username=username, text=text, filename=filename)
        loop = self.config.client.loop
        asyncio.run_coroutine_threadsafe(coro, loop).result()

    async def _send_msg(self, channelname, text, filename=None):
        channel = self.config.get_channel_named(channelname)
        if channel is None:
            error_msg = "チャンネル名(%s)が不正です\nchannels: %s" % (channelname, self.config.get_channelnames())
            raise CLBError(error_msg)
        client = self.config.client
        if filename is None:
            await client.send_message(destination=channel, content=text)
        else:
            await client.send_file(destination=channel, fp=filename, content=text)

    async def _send_dm(self, username, text, filename=None):
        user = self.config.get_user_named(username)
        if user is None:
            error_msg = "ユーザー名(%s)が不正です\nusers: %s" % (username, self.config.get_usernames())
            raise CLBError(error_msg)
        client = self.config.client
        if filename is None:
            await client.send_message(destination=user, content=text)
        else:
            await client.send_file(destination=user, fp=filename, content=text)

    def kill(self) -> None:
        client = self.config.client
        if client.is_logged_in:
            asyncio.run_coroutine_threadsafe(client.logout(), client.loop)


class DiscordFrontEnd:
    def __init__(self,
                 init_cmd: str = "!init",
                 data_path: str = "~/.clbconfig.json",
                 data_category: str = "discord") -> None:
        # configの準備
        data = CLBData(path=data_path)
        client = discord.Client()
        self.config = DiscordConfig(client, data, data_category)
        # input/output frontendの作成
        self.input_frontend = DiscordInputFrontEnd(self.config, init_cmd)
        self.output_frontend = DiscordOutputFrontEnd(self.config)
