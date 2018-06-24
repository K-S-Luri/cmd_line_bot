from typing import Optional
from abc import ABCMeta, abstractmethod


# コマンドライン
# 主に input frontend 絡みのAPIで用いる
class CLBCmdLine(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self,
                 content: str,
                 author: str) -> None:
        self.content = content
        self.author = author

    @abstractmethod
    def get_info(self) -> str:
        pass


class CLBCmdLine_Msg(CLBCmdLine):
    def __init__(self,
                 content: str,
                 author: str,
                 channelname: str) -> None:
        super(CLBCmdLine_Msg, self).__init__(content, author)
        self.channelname = channelname

    def get_info(self) -> str:
        return "[msg from %s in %s] %s" % (self.author, self.channelname, self.content)


class CLBCmdLine_DM(CLBCmdLine):
    def __init__(self,
                 content: str,
                 author: str) -> None:
        super(CLBCmdLine_DM, self).__init__(content, author)

    def get_info(self) -> str:
        return "[dm from %s] %s" % (self.author, self.content)


class CLBDummyCmdLine(CLBCmdLine):
    def __init__(self):
        pass

    def get_info(self) -> str:
        return "dummy"


# タスク
# output frontend にメッセージの送信を依頼する際に用いる
class CLBTask(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self,
                 text: Optional[str] = None,
                 filename: Optional[str] = None,
                 cmdline: Optional[CLBCmdLine] = None) -> None:
        self.text = text
        self.filename = filename
        self.cmdline = cmdline


class CLBTask_Msg(CLBTask):
    def __init__(self,
                 channelname: str,
                 text: Optional[str],
                 filename: Optional[str] = None,
                 cmdline: Optional[CLBCmdLine] = None) -> None:
        super(CLBTask_Msg, self).__init__(text, filename, cmdline)
        self.channelname = channelname


class CLBTask_DM(CLBTask):
    def __init__(self,
                 username: str,
                 text: Optional[str],
                 filename: Optional[str] = None,
                 cmdline: Optional[CLBCmdLine] = None) -> None:
        super(CLBTask_DM, self).__init__(text, filename, cmdline)
        self.username = username


class CLBDummyTask(CLBTask):
    def __init__(self):
        pass


# utilities
def create_reply_task(cmdline: CLBCmdLine,
                      text: Optional[str] = None,
                      filename: Optional[str] = None) -> CLBTask:
    if isinstance(cmdline, CLBCmdLine_Msg):
        channelname = cmdline.channelname
        task = CLBTask_Msg(channelname=channelname,
                           text=text,
                           filename=filename,
                           cmdline=cmdline)  # type: CLBTask
    elif isinstance(cmdline, CLBCmdLine_DM):
        author = cmdline.author
        task = CLBTask_DM(username=author,
                          text=text,
                          filename=filename,
                          cmdline=cmdline)
    return task
