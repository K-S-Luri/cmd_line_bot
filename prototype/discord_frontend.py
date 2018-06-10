#!/usr/bin/env python3
import discord
from cmd_line_bot import CLBFrontEnd
from clb_error import CLBError
from clb_data import CLBData

class DiscordFrontEnd(CLBFrontEnd):
    def __init__(self, token, init_cmd="!init", data_path="~/.clbrc", data_category="discord"):
        self.token = token
        self.init_cmd = init_cmd
        data = CLBData(path=data_path)
        client = discord.Client()
        self.config = DiscordConfig(client, data, data_category)
        @client.event
        async def on_ready():
            print("logged in as")
            print("[name] %s" % client.user.name)
            print("[ id ] %s" % client.user.id)
            print("------")
    def run(self, callback):
        client = self.config.client
        @client.event
        async def on_message(msg):
            try:
                if msg.content == self.init_cmd:
                    await self.init_client(msg)
                await callback(msg.content)
            except CLBError as e:
                await self.config.reply_to_msg(e.get_msg_to_discord(), msg)
            except Exception as e:
                import traceback
                await self.config.reply_to_msg(traceback.format_exc(), msg)
                raise e
        client.run(self.token)
    async def send_msg(self, channel, text):
        channel = self.config.get_channel_named(channel)
        if channel is None:
            raise CLBError("チャンネル名が不正です")
        await self.config.client.send_message(destination=channel, content=text)
    async def send_dm(self, user, text):
        user = self.config.get_user_named(user)
        if user is None:
            raise CLBError("ユーザー名が不正です")
        await self.config.client.send_message(destination=user, content=text)
    async def init_client(self, msg):
        if msg.server is None:
            raise CLBError("`%s`は(DMではなく，サーバー内の)テキストチャンネルに送信してください" % self.init_cmd)
        print("[Initialize client]\nServer: %s" % msg.server)
        self.config.set_server(msg.server)
        self.config.save()
        await self.config.reply_to_msg("initしました", msg)

class DiscordConfig:
    def __init__(self, client, data, data_category):
        assert isinstance(client, discord.Client)
        assert isinstance(data, CLBData)
        self.client = client
        self.data = data
        self.data_category = data_category
        self.data.add_category(data_category)
        self.server = None
    def get_server(self):
        if self.server is None:
            servername = self.data.get(self.data_category, "servername")
            self.set_server_named(servername)
        return self.server
    def set_server(self, server):
        assert isinstance(server, discord.Server)
        self.server = server
        self.data.set(self.data_category, "servername", server.name)
    def set_server_named(self, servername):
        servers = self.client.servers
        for server in servers:
            if servername == server.name:
                self.set_server(server)
                return True
        return False
    async def reply_to_msg(self, text, msg):
        await self.client.send_message(msg.channel, text)
    def get_channel_named(self, channelname):
        server = self.get_server()
        if server is None:
            return None
        channels = server.channels
        for channel in channels:
            if channelname == channel.name:
                return channel
        return None
    def get_user_named(self, username):
        server = self.get_server()
        if server is None:
            return None
        return server.get_member_named(username)
    def save(self):
        self.data.save()
