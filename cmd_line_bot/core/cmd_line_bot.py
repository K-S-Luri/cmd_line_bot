#!/usr/bin/env python3
from abc import ABCMeta, abstractmethod
import asyncio
from threading import Thread, Event
from queue import Queue
from typing import Callable, Any, List, Union, Optional, cast
# from pytypes import typechecked
import traceback

from .clb_error import CLBError  # , CLBIndexError
from .clb_interface import (CLBTask, CLBTask_Msg, CLBTask_DM, CLBTask_Gathered, CLBDummyTask,
                            CLBCmdLine, CLBCmdLine_Msg, CLBCmdLine_DM, CLBDummyCmdLine,
                            create_reply_task)
from .error_visualizer import traceback_to_terminal


class CLBInputFrontEnd(metaclass=ABCMeta):
    @abstractmethod
    def run(self, callback: Callable[[CLBCmdLine], None]) -> None:
        pass

    @abstractmethod
    def kill(self) -> None:
        pass


class CLBOutputFrontEnd(metaclass=ABCMeta):
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

    def send(self,
             task: CLBTask) -> None:
        if isinstance(task, CLBTask_Msg):
            self.send_msg(channelname=task.channelname,
                          text=task.text,
                          filename=task.filename)
        elif isinstance(task, CLBTask_DM):
            self.send_dm(username=task.username,
                         text=task.text,
                         filename=task.filename)
        elif isinstance(task, CLBTask_Gathered):
            print("複数メッセージの並列送信はまだ対応してないよ")
            for t in task:
                self.send(t)

    @abstractmethod
    def kill(self) -> None:
        pass


class CLBBackEnd(metaclass=ABCMeta):
    @abstractmethod
    def manage_cmdline(self,
                       cmdline: CLBCmdLine,
                       send_task: Callable[[CLBTask], None]) -> None:
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
        self.queue = Queue()  # type: Queue[CLBTask]
        self._killed = False

    def run(self):
        while True:
            task = self.queue.get()
            if self._killed:
                break
            try:
                self.output_frontend.send(task)
                send_success = True
            except CLBError as e:
                cmdline = task.cmdline
                if cmdline is None:
                    raise CLBError("cmdlineがNoneです．発言元にエラーメッセージを返せるよう，CLBTaskにはcmdlineを設定してください")
                error_msg = e.get_msg_to_discord()
                error_task = create_reply_task(cmdline, error_msg)
                send_success = False
            except FileNotFoundError as e:
                print(traceback.format_exc())
                cmdline = task.cmdline
                error_msg = "File Not Found: %s" % task.filename
                error_task = create_reply_task(cmdline, error_msg)
                send_success = False
            except Exception as e:
                cmdline = task.cmdline
                error_msg = traceback.format_exc()
                print(cmdline.get_info())
                print(error_msg)
                # error_msg_format = "```\n%s```" % error_msg  # code block にすると変なところで改行される
                error_task = create_reply_task(cmdline, error_msg)
                send_success = False
            finally:
                if not send_success:
                    try:
                        self.output_frontend.send(error_task)
                    except CLBError as e_:
                        print("%sをfrontendに送信する過程でエラー1が発生し，" % task)
                        print("さらにエラー1の情報をfrontendに送信する過程でエラー2が発生しました")
                        print("[エラー1]", error_msg)
                        print("[エラー2]", e_.get_msg_to_discord())
                        print(traceback.format_exc())

    def put(self,
            task: CLBTask) -> None:
        self.queue.put(task)

    def kill(self) -> None:
        self._killed = True
        self.queue.put(CLBDummyTask())
        self.output_frontend.kill()


class CLBBackEndThread(Thread):
    def __init__(self,
                 backend: CLBBackEnd,
                 callback: Callable[[CLBTask], None]) -> None:
        super(CLBBackEndThread, self).__init__()
        self.setDaemon(False)
        self.backend = backend
        self.queue = Queue()  # type: Queue[CLBCmdLine]
        self.callback = callback
        self._killed = False

    def run(self) -> None:
        while True:
            cmdline = self.queue.get()
            if self._killed:
                break
            try:
                self.backend.manage_cmdline(cmdline, self.callback)
            except CLBError as e:
                error_msg = e.get_msg_to_discord()
                task = create_reply_task(cmdline=cmdline, text=error_msg, filename=None)
                self.callback(task)
                # print(error_msg)
            except Exception as e:
                error_msg = traceback.format_exc()
                # error_msg_format = "```\n%s\n```" % error_msg  # code block にすると変なところで改行される
                task = create_reply_task(cmdline=cmdline, text=error_msg, filename=None)
                self.callback(task)
                print(cmdline.get_info())
                error_msg_to_termianl = traceback_to_terminal()
                print(error_msg_to_termianl)

    def put(self, cmdline: CLBCmdLine) -> None:
        self.queue.put(cmdline)

    def kill(self) -> None:
        self._killed = True
        self.queue.put(CLBDummyCmdLine())
        self.backend.kill()


class CmdLineBot:
    def __init__(self,
                 input_frontend: Union[CLBInputFrontEnd, List[CLBInputFrontEnd]],
                 output_frontend: CLBOutputFrontEnd,
                 backend: CLBBackEnd) -> None:
        # ends
        if isinstance(input_frontend, CLBInputFrontEnd):
            input_frontend = [input_frontend]
        self.input_frontends = input_frontend
        self.output_frontend = output_frontend
        self.backend = backend
        # threads
        def create_ifet(ife):
            return CLBInputFrontEndThread(ife, self.callback_from_inputfrontend)
        self.input_frontend_threads = list(map(create_ifet, self.input_frontends))
        self.output_frontend_thread = CLBOutputFrontEndThread(output_frontend)
        self.backend_thread = CLBBackEndThread(self.backend, self.callback_from_backend)
        self.threads = self.input_frontend_threads + [self.output_frontend_thread,
                                                      self.backend_thread]

    def run(self) -> None:
        for thread in self.threads:
            thread.start()
        import time
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            for thread in self.threads:
                thread.kill()

    def callback_from_inputfrontend(self, cmdline: CLBCmdLine) -> None:
        self.backend_thread.put(cmdline)

    def callback_from_backend(self, task: CLBTask) -> None:
        self.output_frontend_thread.put(task)
