from ..core.cmd_line_bot import CLBInputFrontEnd, CLBOutputFrontEnd
from ..core.clb_interface import CLBCmdLine_Msg, CLBCmdLine_DM


class TerminalInputFrontEnd(CLBInputFrontEnd):
    def __init__(self):
        pass

    def run(self, callback):
        while True:
            content = input("content: ")
            channelname = "general"
            author = "Bourbaki"
            cmdline = CLBCmdLine_Msg(content, author, channelname)
            callback(cmdline)

    def kill(self):
        pass


linesep = "----------\n"


class TerminalOutputFrontEnd(CLBOutputFrontEnd):
    def send_msg(self, channelname, text, filename=None):
        if filename is None:
            fileinfo = ""
        else:
            fileinfo = " attached: {filename}".format(filename=filename)
        print(linesep + "[{channelname}]{fileinfo}\n{text}".format(channelname=channelname,
                                                                   fileinfo=fileinfo,
                                                                   text=text))

    def send_dm(self, username, text, filename=None):
        if filename is None:
            fileinfo = ""
        else:
            fileinfo = " attached: {filename}".format(filename=filename)
        print(linesep + "<DM@{username}>{fileinfo}\n{text}".format(username=username,
                                                                   fileinfo=fileinfo,
                                                                   text=text))

    def kill(self):
        pass
