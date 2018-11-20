#!/usr/bin/env python3
import asyncio
from time import sleep

from ..core.cmd_line_bot import CLBInputFrontEnd, CLBOutputFrontEnd, CLBBackEnd, CLBTask
from ..core.clb_interface import CLBCmdLine, CLBCmdLine_Msg, CLBTask_Msg, CLBTask_DM, create_reply_task


linesep = "----------\n"


class TrivialInputFrontEnd(CLBInputFrontEnd):
    def run(self, callback):
        print("This is TrivialInputFrontEnd")
        # loop = asyncio.get_event_loop()
        contents = ["!dm wktkshn private", "!msg general hogeeeee", "!file general fugafuga"]
        for content in contents:
            cmdline = CLBCmdLine_Msg(content=content, author="bourbaki", channelname="mychannel")
            callback(cmdline)

    def kill(self):
        pass


class TrivialOutputFrontEnd(CLBOutputFrontEnd):
    def send_msg(self, channelname, text, filename=None):
        if filename is None:
            fileinfo = ""
        else:
            fileinfo = " attached: %s" % filename
        print(linesep + "[%s]%s\n%s" % (channelname, fileinfo, text))

    def send_dm(self, username, text, filename=None):
        if filename is None:
            fileinfo = ""
        else:
            fileinfo = " attached: %s" % filename
        print(linesep + "<DM@%s>%s\n%s" % (username, fileinfo, text))

    def kill(self):
        pass


class TrivialBackEnd(CLBBackEnd):
    def manage_cmdline(self, cmdline, send_task):
        assert isinstance(cmdline, CLBCmdLine)
        parsed = self.parse_cmdline(cmdline.content)
        if parsed is None:
            return []
        cmd = parsed[0]
        if len(parsed) <= 1:
            return
        name = parsed[1]
        text = "%s\n%s" % (cmdline.get_info(), parsed[2])
        send_task(create_reply_task(cmdline, text))
        # tasks = []
        # if cmd == "dm":
        #     # tasks.append(CLBTask(tasktype="dm", username=name, text=text))
        #     send_task(create_reply_task(cmdline, text))
        # if cmd == "msg":
        #     # tasks.append(CLBTask(tasktype="msg", channelname=name, text=text))
        #     send_task(CLBTask(tasktype="msg", channelname=name, text=text))
        # if cmd == "file":
        #     # tasks.append(CLBTask(tasktype="msg", channelname=name, text=text, filename="dice.png"))
        #     send_task(CLBTask(tasktype="msg", channelname=name, text=text, filename="dice.png"))
        # # return tasks

    def parse_cmdline(self, cmdline):
        if not cmdline.startswith("!"):
            return None
        return cmdline[1:].split()

    def kill(self):
        pass
