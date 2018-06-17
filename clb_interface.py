from typing import Optional

# API用のクラス
class CLBTask:
    # msg と dm で分けてサブクラスを作った方が良いかも
    def __init__(self, tasktype: str,
                 username: Optional[str] = None,
                 channelname: Optional[str] = None,
                 text: Optional[str] = None,
                 filename: Optional[str] = None) -> None:
        self.type = tasktype
        self.username = username
        self.channelname = channelname
        self.text = text
        self.filename = filename

class CLBCmdLine:
    def __init__(self, cmdline_type: str,
                 content: str,
                 author: str,
                 channelname: Optional[str] = None) -> None:
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
