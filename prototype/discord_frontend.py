#!/usr/bin/env python3
import discord
from cmd_line_bot import CLBFrontEnd

class DiscordFrontEnd(CLBFrontEnd):
    def __init__(self, token):
        self.token = token
        client = discord.Client()
        self.client = client
        @client.event
        async def on_ready():
            print("logged in as")
            print("[name] %s" % client.user.name)
            print("[ id ] %s" % client.user.id)
            # self.server = list(client.servers)[0]
            # self.channel = list(self.server.channels)[0]
            print("------")
    def run(self, callback):
        client = self.client
        @client.event
        async def on_message(msg):
            if msg.content == "init":
                self.init_client(msg)
            await callback(msg.content)
        client.run(self.token)
    async def send_msg(self, channel, text):
        await self.client.send_message(destination=self.channel,
                                       content=text)
    async def send_dm(self, user, text):
        pass
    def init_client(self, msg):
        if msg.server is None:
            print("initは(DMではなく)テキストチャンネルに送信してください")
            return
        print("[Initialize client]\nServer: %s, Channel: %s" % (msg.server, msg.channel))
        self.server = msg.server
        self.channel = msg.channel
