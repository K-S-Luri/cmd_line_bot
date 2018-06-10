#!/usr/bin/env python3
from abc import ABCMeta, abstractmethod
import asyncio

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
