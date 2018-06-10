#!/usr/bin/env python3
from abc import ABCMeta, abstractmethod
import asyncio
import discord

class CmdLineBot:
    def __init__(self, frontend, backend):
        if not isinstance(frontend, CLBFrontEnd):
            raise Exception("frontendはCLBFrontEndを継承している必要があります")
        if not isinstance(backend, CLBBackEnd):
            raise Exception("backendはCLBBackEndを継承している必要があります")
        self.frontend = frontend
        self.backend = backend
    def run(self):
        self.frontend.run(self.call_backend)
    async def call_backend(self, cmdline):
        tasks = self.backend.manage_cmdline(cmdline)
        loop = asyncio.get_event_loop()
        for task in tasks:
            if task["type"] == "msg":
                await self.frontend.send_msg(channel=task["channel"], text=task["text"])
            elif task["type"] == "dm":
                await self.frontend.send_dm(user=task["user"], text=task["text"])

class CLBFrontEnd(metaclass=ABCMeta):
    def __init__(self):
        pass
    @abstractmethod
    def run(self, callback):
        pass
    @abstractmethod
    async def send_msg(self, channel, text):
        pass
    @abstractmethod
    async def send_dm(self, user, text):
        pass

class CLBBackEnd(metaclass=ABCMeta):
    def __init__(self):
        pass
    @abstractmethod
    def manage_cmdline(self, cmdline):
        pass

# 具体的実装
class MyFrontEnd(CLBFrontEnd):
    def run(self, callback):
        print("This is MyFrontEnd")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(callback("dm user1 private"))
        loop.run_until_complete(callback("msg ch1 open"))
    async def send_msg(self, channel, text):
        print("[%s] %s" % (channel, text))
    async def send_dm(self, user, text):
        print("<DM@%s> %s" % (user, text))

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

class MyBackEnd(CLBBackEnd):
    def manage_cmdline(self, cmdline):
        # print("backend: " + cmdline)
        parsed = self.parse_cmdline(cmdline)
        cmd = parsed[0]
        tasks = []
        if cmd == "dm":
            tasks.append({"type": "dm",
                          "user": parsed[1],
                          "text": parsed[2]})
        if cmd == "msg":
            tasks.append({"type": "msg",
                          "channel": parsed[1],
                          "text": parsed[2]})
        return tasks
    def parse_cmdline(self, cmdline):
        return cmdline.split()

# メイン
def main():
    token = "NDU1Mjg1OTQwODQ0NDk0ODUw.Df5zIw.Qy0amuaPNJSVSEH30o0H3Gm4e1Y"
    frontend = MyFrontEnd()
    frontend = DiscordFrontEnd(token)
    backend = MyBackEnd()
    clb = CmdLineBot(frontend, backend)
    clb.run()

if __name__ == '__main__':
    main()
