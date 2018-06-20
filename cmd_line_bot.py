#!/usr/bin/env python3
from abc import ABCMeta, abstractmethod
import asyncio
from threading import Thread, Event
from queue import Queue
from typing import Callable, Any, List, Union, Optional, cast
# from pytypes import typechecked
import traceback

from clb_error import CLBError  # , CLBIndexError
from clb_interface import CLBTask, CLBDummyTask, CLBDummyCmdLine, CLBCmdLine, create_reply_task


class CLBInputFrontEnd(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def run(self, callback: Callable[[CLBCmdLine], None]) -> None:
        pass

    @abstractmethod
    def kill(self) -> None:
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

    @abstractmethod
    def kill(self) -> None:
        pass


class CLBBackEnd(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def manage_cmdline(self, cmdline: CLBCmdLine) -> List[Union[CLBTask, List[CLBTask]]]:
        pass

    @abstractmethod
    def kill(self) -> None:
        pass


# threads
class CLBInputFrontEndThread(Thread):
    def __init__(self,
                 input_frontend: CLBInputFrontEnd,
                 callback: Callable[[CLBCmdLine], None]) -> None:
        super(CLBInputFrontEndThread, self).__init__()
        self.setDaemon(False)
        self.input_frontend = input_frontend
        self.callback = callback

    def run(self) -> None:
        self.input_frontend.run(self.callback)

    def kill(self) -> None:
        self.input_frontend.kill()


class CLBOutputFrontEndThread(Thread):
    def __init__(self,
                 output_frontend: CLBOutputFrontEnd) -> None:
        super(CLBOutputFrontEndThread, self).__init__()
        self.setDaemon(False)
        self.output_frontend = output_frontend
        self.queue = Queue()  # type: Queue[Union[CLBTask, List[CLBTask]]]
        self._killed = False

    def run(self):
        while True:
            task_group = self.queue.get()
            if self._killed:
                break
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

    def kill(self) -> None:
        self._killed = True
        self.queue.put(CLBDummyTask())
        self.output_frontend.kill()


class CLBBackEndThread(Thread):
    def __init__(self,
                 backend: CLBBackEnd,
                 callback: Callable[[Union[CLBTask, List[CLBTask]]], None]) -> None:
        super(CLBBackEndThread, self).__init__()
        self.setDaemon(False)
        self.backend = backend
        self.queue = Queue()  # type: Queue[CLBCmdLine]
        self.callback = callback
        self._killed = False

    def run(self):
        while True:
            cmdline = self.queue.get()
            if self._killed:
                break
            try:
                tasks = self.backend.manage_cmdline(cmdline)
                for task_group in tasks:
                    self.callback(task_group)
            except CLBError as e:
                error_msg = e.get_msg_to_discord()
                task = create_reply_task(cmdline=cmdline, text=error_msg, filename=None)
                self.callback(task)
                # print(error_msg)
            except Exception as e:
                error_msg = traceback.format_exc()
                task = create_reply_task(cmdline=cmdline, text=error_msg, filename=None)
                self.callback(task)
                if cmdline.type == "msg":
                    info = "msg from %s in %s" % (cmdline.author, cmdline.channelname)
                elif cmdline.type == "dm":
                    info = "dm from %s" % cmdline.author
                print("[%s] %s" % (info, cmdline.content))
                print(error_msg)

    def put(self, cmdline: CLBCmdLine) -> None:
        self.queue.put(cmdline)

    def kill(self) -> None:
        self._killed = True
        self.queue.put(CLBDummyCmdLine())
        self.backend.kill()


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
        # self.input_frontend.run(self.callback_from_inputfrontend)
        self.input_frontend_thread = CLBInputFrontEndThread(self.input_frontend, self.callback_from_inputfrontend)
        self.input_frontend_thread.start()
        import time
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            self.input_frontend_thread.kill()
            self.output_frontend_thread.kill()
            self.backend_thread.kill()

    def callback_from_inputfrontend(self, cmdline: CLBCmdLine) -> Any:  # 返り値はNoneに直す
        self.backend_thread.put(cmdline)

    def callback_from_backend(self, task_group: Union[CLBTask, List[CLBTask]]) -> None:
        self.output_frontend_thread.put(task_group)
