#!/usr/bin/env python3
from abc import ABCMeta, abstractmethod
import asyncio
from typing import Callable, Coroutine, Any, List, Union, Optional, cast
from pytypes import typechecked

from clb_error import CLBError, CLBIndexError
from clb_interface import CLBTask, CLBCmdLine


class CLBFrontEnd(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def run(self, callback: Callable[[CLBCmdLine],
                                     Coroutine[Any, Any, None]]) -> None:
        pass

    @abstractmethod
    async def send_msg(self,
                       channelname: str,
                       text: Optional[str],
                       filename: Optional[str]) -> None:
        pass

    @abstractmethod
    async def send_dm(self,
                      username: str,
                      text: Optional[str],
                      filename: Optional[str]) -> None:
        pass


class CLBBackEnd(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def manage_cmdline(self, cmdline: CLBCmdLine) -> List[Union[CLBTask, List[CLBTask]]]:
        pass


class CmdLineBot:
    def __init__(self, frontend: CLBFrontEnd, backend: CLBBackEnd) -> None:
        self.frontend = frontend
        self.backend = backend

    def run(self) -> None:
        self.frontend.run(self.call_backend)

    async def call_backend(self, cmdline: CLBCmdLine) -> None:
        tasks = self.backend.manage_cmdline(cmdline)
        assert isinstance(tasks, list), "%s is not a list" % tasks
        for task_group in tasks:
            coroutines = []
            if isinstance(task_group, CLBTask):
                task_group = [task_group]
            for task in task_group:
                if task.type == "msg":
                    channelname = cast(str, task.channelname)
                    coroutines.append(self.frontend.send_msg(channelname=channelname,
                                                             text=task.text,
                                                             filename=task.filename))
                elif task.type == "dm":
                    username = cast(str, task.username)
                    coroutines.append(self.frontend.send_dm(username=username,
                                                            text=task.text,
                                                            filename=task.filename))
            await asyncio.gather(*coroutines)
