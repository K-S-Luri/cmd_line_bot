#!/usr/bin/env python3
from abc import ABCMeta, abstractmethod
import asyncio
from clb_error import CLBError, CLBIndexError

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
        assert isinstance(cmdline, CLBCmdLine), "%s is not a CLBCmdLine" % cmdline
        tasks = self.backend.manage_cmdline(cmdline)
        assert isinstance(tasks, list), "%s is not a list" % tasks
        for task_group in tasks:
            coroutines = []
            if isinstance(task_group, CLBTask):
                task_group = [task_group]
            for task in task_group:
                if task.type == "msg":
                    coroutines.append(self.frontend.send_msg(channelname=task.channelname, text=task.text, filename=task.filename))
                elif task.type == "dm":
                    coroutines.append(self.frontend.send_dm(username=task.username, text=task.text, filename=task.filename))
            await asyncio.gather(*coroutines)

class CLBFrontEnd(metaclass=ABCMeta):
    def __init__(self):
        pass
    @abstractmethod
    def run(self, callback):
        pass
    @abstractmethod
    async def send_msg(self, channelname, text, filename):
        pass
    @abstractmethod
    async def send_dm(self, username, text, filename):
        pass

class CLBBackEnd(metaclass=ABCMeta):
    def __init__(self):
        pass
    @abstractmethod
    def manage_cmdline(self, cmdline):
        pass

# API用のクラス
class CLBTask:
    def __init__(self, tasktype, username=None, channelname=None, text=None, filename=None):
        self.type = tasktype
        self.username = username
        self.channelname = channelname
        self.text = text
        self.filename = filename

class CLBCmdLine:
    def __init__(self, cmdline_type, content, author, channelname=None):
        assert cmdline_type in ["msg", "dm"]
        assert isinstance(content, str) and isinstance(author, str)
        if cmdline_type == "msg":
            assert isinstance(channelname, str)
        elif cmdline_type == "dm":
            assert channelname is None
        self.type = cmdline_type
        self.content = content
        self.author = author
        self.channelname = channelname
