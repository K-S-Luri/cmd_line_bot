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
    def __init__(self, cmdline_type, content, author):
        self.type = cmdline_type # "msg", "dm"
        self.content = content
        self.author = author
    def parse(self, parser):
        self.parsed_content = parser(self.content)
        if self.parsed_content is None:
            return
        assert isinstance(self.parsed_content, list)
        assert len(self.parsed_content) > 0
    def get_nth_content(self, nth):
        if not hasattr(self, "parsed_content"):
            raise CLBError("先にparseして下さい")
        assert self.parsed_content is not None
        if nth >= len(self.parsed_content):
            raise CLBIndexError("不正なindexです")
        return self.parsed_content[nth]
    def get_after_nth_content(self, nth):
        return self.parsed_content[nth+1:]
    def len_parsed_content(self):
        return len(self.parsed_content)
    def get_num_args(self, pointer):
        return len(self.parsed_content) - pointer - 1
    def get_args(self, pointer):
        assert self.get_num_args(pointer) >= 0
        return self.parsed_content[pointer+1:]
