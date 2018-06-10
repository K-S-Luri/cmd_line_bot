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
        for task_group in tasks:
            coroutines = []
            if isinstance(task_group, CLBTask):
                task_group = [task_group]
            for task in task_group:
                if task.type == "msg":
                    coroutines.append(self.frontend.send_msg(channelname=task.channelname, text=task.text))
                elif task.type == "dm":
                    coroutines.append(self.frontend.send_dm(username=task.username, text=task.text))
            await asyncio.gather(*coroutines)

class CLBFrontEnd(metaclass=ABCMeta):
    def __init__(self):
        pass
    @abstractmethod
    def run(self, callback):
        pass
    @abstractmethod
    async def send_msg(self, channelname, text):
        pass
    @abstractmethod
    async def send_dm(self, username, text):
        pass

class CLBBackEnd(metaclass=ABCMeta):
    def __init__(self):
        pass
    @abstractmethod
    def manage_cmdline(self, cmdline):
        pass

# API用のクラス
class CLBTask:
    def __init__(self, tasktype, username=None, channelname=None, text=None):
        self.type = tasktype
        self.username = username
        self.channelname = channelname
        self.text = text
