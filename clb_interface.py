from typing import Optional


# API用のクラス
class CLBCmdLine:
    # CLBTaskと同じく，msg と dm で分けてサブクラスを作る？
    def __init__(self, cmdline_type: str,
                 content: str,
                 author: str,
                 channelname: Optional[str] = None) -> None:
        assert cmdline_type in ["msg", "dm"]
        if cmdline_type == "msg":
            assert isinstance(channelname, str)
        elif cmdline_type == "dm":
            assert channelname is None
        self.type = cmdline_type
        self.content = content
        self.author = author
        self.channelname = channelname


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
    tasktype = cmdline.type
    if tasktype == "msg":
        channelname = cmdline.channelname
        task = CLBTask(tasktype=tasktype, channelname=channelname, text=text, filename=filename, cmdline=cmdline)
    elif tasktype == "dm":
        author = cmdline.author
        task = CLBTask(tasktype=tasktype, username=author, text=text, filename=filename, cmdline=cmdline)
    return task
