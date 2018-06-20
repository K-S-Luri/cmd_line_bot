#!/usr/bin/env python3
from abc import ABCMeta, abstractmethod
import asyncio
from threading import Thread
from queue import Queue
from typing import Callable, Coroutine, Any, List, Union, Optional, cast
from pytypes import typechecked

from clb_error import CLBError, CLBIndexError
from clb_interface import CLBTask, CLBCmdLine


class CLBInputFrontEnd(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def run(self, callback: Callable[[CLBCmdLine],
                                     Coroutine[Any, Any, None]]) -> None:
        pass


class CLBOutputFrontEnd(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def send_msg(self,
                 channelname: str,
                 text: Optional[str],
                 filename: Optional[str]) -> None:
        pass

    @abstractmethod
    def send_dm(self,
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


# threads
class CLBOutputFrontEndThread(Thread):
    def __init__(self,
                 output_frontend: CLBOutputFrontEnd) -> None:
        super(CLBOutputFrontEndThread, self).__init__()
        self.setDaemon(True)
        self.output_frontend = output_frontend
        self.queue = Queue()  # type: Queue[Union[CLBTask, List[CLBTask]]]

    def run(self):
        # loop = asyncio.new_event_loop()
        while True:
            task_group = self.queue.get()
            # coroutines = []
            if isinstance(task_group, CLBTask):
                task_group = [task_group]
            if len(task_group) >= 2:
                print("複数メッセージの並列送信はまだ対応してないよ")
            for task in task_group:
                if task.type == "msg":
                    channelname = cast(str, task.channelname)
                    self.output_frontend.send_msg(channelname=channelname,
                                                  text=task.text,
                                                  filename=task.filename)
                elif task.type == "dm":
                    username = cast(str, task.username)
                    self.output_frontend.send_dm(username=username,
                                                 text=task.text,
                                                 filename=task.filename)

    def put(self,
            task_group: Union[CLBTask, List[CLBTask]]) -> None:
        self.queue.put(task_group)


class CLBBackEndThread(Thread):
    def __init__(self,
                 backend: CLBBackEnd,
                 callback: Callable[[Union[CLBTask, List[CLBTask]]], None]) -> None:
        super(CLBBackEndThread, self).__init__()
        self.setDaemon(True)
        self.backend = backend
        self.queue = Queue()  # type: Queue[CLBCmdLine]
        self.callback = callback

    def run(self):
        while True:
            cmdline = self.queue.get()
            tasks = self.backend.manage_cmdline(cmdline)
            for task_group in tasks:
                self.callback(task_group)

    def put(self, cmdline: CLBCmdLine) -> None:
        self.queue.put(cmdline)


class CmdLineBot:
    def __init__(self,
                 input_frontend: CLBInputFrontEnd,
                 output_frontend: CLBOutputFrontEnd,
                 backend: CLBBackEnd) -> None:
        self.input_frontend = input_frontend
        self.output_frontend = output_frontend
        self.backend = backend
        # output_frontend.config.client.run(output_frontend.token)
        self.output_frontend_thread = CLBOutputFrontEndThread(output_frontend)
        self.backend_thread = CLBBackEndThread(self.backend, self.callback_from_backend)

        threads = [self.output_frontend_thread, self.backend_thread]
        for thread in threads:
            thread.start()

    def run(self) -> None:
        self.input_frontend.run(self.callback_from_inputfrontend)

    def callback_from_inputfrontend(self, cmdline: CLBCmdLine) -> Any:  # 返り値はNoneに直す
        self.backend_thread.put(cmdline)

    def callback_from_backend(self, task_group: Union[CLBTask, List[CLBTask]]) -> None:
        self.output_frontend_thread.put(task_group)
