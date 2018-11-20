from typing import List, Optional
from time import sleep
import os
import shutil

from ..core.cmd_line_bot import CLBInputFrontEnd, CLBOutputFrontEnd
from ..core.clb_interface import CLBCmdLine_Msg, CLBCmdLine_DM


class TerminalInputFrontEnd(CLBInputFrontEnd):
    def __init__(self,
                 msg_list: Optional[List[str]] = None) -> None:
        if msg_list is None:
            msg_list = []
        self.msg_list = msg_list

    def run(self, callback):
        while True:
            if self.msg_list:
                content = self.msg_list.pop(0)
            else:
                sleep(0.5)
                content = input("msg: ")
            channelname = "general"
            author = "Bourbaki"
            cmdline = CLBCmdLine_Msg(content, author, channelname)
            callback(cmdline)

    def kill(self):
        pass


linesep = "----------\n"


class TerminalOutputFrontEnd(CLBOutputFrontEnd):
    def send_msg(self, channelname, text, filename=None):
        destination_str = "[%s]" % channelname
        self._send_msg_or_dm(destination_str, text, filename)

    def send_dm(self, username, text, filename=None):
        destination_str = "<DM@%s>" % username
        self._send_msg_or_dm(destination_str, text, filename)

    def _send_msg_or_dm(self,
                        destination_str: str,
                        text: str,
                        filename: Optional[str]) -> None:
        if filename is None:
            fileinfo = ""
        else:
            fileinfo = " attached: {filename}".format(filename=filename)
            if shutil.which("xdg-open"):
                os.system("xdg-open {filename} &".format(filename=filename))
        print(linesep + "{destination}{fileinfo}\n{text}".format(destination=destination_str,
                                                                 fileinfo=fileinfo,
                                                                 text=text))

    def kill(self):
        pass
