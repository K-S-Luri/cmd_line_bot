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
        res = self.backend.manage_cmdline(cmdline)
        for r in res:
            if r["type"] == "msg":
                await self.frontend.send_msg(channel=r["channel"], text=r["text"])
            elif r["type"] == "dm":
                await self.frontend.send_dm(user=r["user"], text=r["text"])

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
            self.server = list(client.servers)[0]
            self.channel = list(self.server.channels)[0]
            print("------")
    def run(self, callback):
        client = self.client
        @client.event
        async def on_message(msg):
            await callback(msg.content)
        client.run(self.token)
    async def send_msg(self, channel, text):
        await self.client.send_message(destination=self.channel,
                                       content=text)
    async def send_dm(self, user, text):
        pass

class MyBackEnd(CLBBackEnd):
    def manage_cmdline(self, cmdline):
        # print("backend: " + cmdline)
        parsed = self.parse_cmdline(cmdline)
        cmd = parsed[0]
        if cmd == "dm":
            return [{"type": "dm",
                     "user": parsed[1],
                     "text": parsed[2]}]
        if cmd == "msg":
            return [{"type": "msg",
                     "channel": parsed[1],
                     "text": parsed[2]},
                    {"type": "msg",
                     "channel": parsed[1],
                     "text": parsed[2]}]
        return []
    def parse_cmdline(self, cmdline):
        return cmdline.split()

# メイン
def main():
    token = "NDU1Mjg1OTQwODQ0NDk0ODUw.Df5zIw.Qy0amuaPNJSVSEH30o0H3Gm4e1Y"
    frontend = DiscordFrontEnd(token)
    # frontend = MyFrontEnd()
    backend = MyBackEnd()
    clb = CmdLineBot(frontend, backend)
    clb.run()

def _main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_main())

if __name__ == '__main__':
    main()
