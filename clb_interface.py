from typing import Optional
from abc import ABCMeta, abstractmethod


# API用のクラス
class CLBCmdLine(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self,
                 content: str,
                 author: str) -> None:
        self.content = content
        self.author = author


class CLBCmdLine_Msg(CLBCmdLine):
    def __init__(self,
                 content: str,
                 author: str,
                 channelname: str) -> None:
        super(CLBCmdLine_Msg, self).__init__(content, author)
        self.channelname = channelname


class CLBCmdLine_DM(CLBCmdLine):
    def __init__(self,
                 content: str,
                 author: str) -> None:
        super(CLBCmdLine_DM, self).__init__(content, author)


class CLBDummyCmdLine(CLBCmdLine):
    def __init__(self):
        pass


class CLBTask:
    # msg と dm で分けてサブクラスを作った方が良いかも
    def __init__(self, tasktype: str,
                 username: Optional[str] = None,
                 channelname: Optional[str] = None,
                 text: Optional[str] = None,
                 filename: Optional[str] = None,
                 cmdline: Optional[CLBCmdLine] = None) -> None:
        self.type = tasktype
        self.username = username
        self.channelname = channelname
        self.text = text
        self.filename = filename
        self.cmdline = cmdline


class CLBDummyTask(CLBTask):
    def __init__(self):
        pass


# utilities
def create_reply_task(cmdline: CLBCmdLine,
                      text: Optional[str] = None,
                      filename: Optional[str] = None) -> CLBTask:
    if isinstance(cmdline, CLBCmdLine_Msg):
        tasktype = "msg"
        channelname = cmdline.channelname
        task = CLBTask(tasktype=tasktype, channelname=channelname, text=text, filename=filename, cmdline=cmdline)
    elif isinstance(cmdline, CLBCmdLine_DM):
        tasktype = "dm"
        author = cmdline.author
        task = CLBTask(tasktype=tasktype, username=author, text=text, filename=filename, cmdline=cmdline)
    return task
