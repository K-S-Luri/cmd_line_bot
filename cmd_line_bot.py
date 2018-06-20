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


# threads
class CLBOutputFrontEndThread(Thread):
    def __init__(self,
                 frontend: CLBOutputFrontEnd) -> None:
        super(CLBOutputFrontEndThread, self).__init__()
        self.setDaemon(True)
        self.frontend = frontend
        self.queue = Queue()  # type: Queue[Union[CLBTask, List[CLBTask]]]

    def run(self):
        # loop = asyncio.new_event_loop()
        while True:
            task_group = self.queue.get()
            print("queue of outputFrontend")
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
            # await asyncio.gather(*coroutines)
            # loop.run_until_complete(*coroutines)
            # loop.run_until_complete(self.frontend.send_msg(channelname="general", text="hogeeee", filename=None))
            print("hgoe")
            # asyncio.run_coroutine_threadsafe(self.frontend.send_msg(channelname="general",
            #                                                         text="hogeeee", filename=None),
            #                                  self.frontend.config.client.loop).result()
            for coro in coroutines:
                asyncio.run_coroutine_threadsafe(coro,
                                                 self.frontend.config.client.loop)
            print("finished")

    def put(self,
            task_group: Union[CLBTask, List[CLBTask]]) -> None:
        print("put at outputFrontend")
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
            print("get")
            tasks = self.backend.manage_cmdline(cmdline)
            for task_group in tasks:
                self.callback(task_group)

    def put(self, cmdline: CLBCmdLine) -> None:
        print("put at backend")
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
        self.out_front_thread = CLBOutputFrontEndThread(output_frontend)
        self.back_thread = CLBBackEndThread(self.backend, self.callback_from_backend)

        threads = [self.out_front_thread, self.back_thread]
        for thread in threads:
            thread.start()

    def run(self) -> None:
        self.input_frontend.run(self.callback_from_inputfrontend)

    def callback_from_inputfrontend(self, cmdline: CLBCmdLine) -> Any:  # 返り値はNoneに直す
        self.back_thread.put(cmdline)

    def callback_from_backend(self, task_group: Union[CLBTask, List[CLBTask]]) -> None:
        self.out_front_thread.put(task_group)

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
                    coroutines.append(self.output_frontend.send_msg(channelname=channelname,
                                                                    text=task.text,
                                                                    filename=task.filename))
                elif task.type == "dm":
                    username = cast(str, task.username)
                    coroutines.append(self.output_frontend.send_dm(username=username,
                                                                   text=task.text,
                                                                   filename=task.filename))
            await asyncio.gather(*coroutines)
