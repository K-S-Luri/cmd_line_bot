#!/usr/bin/env python3
import asyncio
from cmd_line_bot import CLBFrontEnd, CLBBackEnd, CLBTask, CLBCmdLine

linesep = "----------\n"

class MyFrontEnd(CLBFrontEnd):
    def run(self, callback):
        print("This is MyFrontEnd")
        loop = asyncio.get_event_loop()
        contents = ["!dm user1 private", "!msg ch1 open", "!file ch2 hoge"]
        for content in contents:
            cmdline = CLBCmdLine(cmdline_type="msg", content=content, author="dummy")
            loop.run_until_complete(callback(cmdline))
    async def send_msg(self, channelname, text, filename=None):
        if filename is None:
            fileinfo = ""
        else:
            fileinfo = " attached: %s" % filename
        print(linesep + "[%s]%s\n%s" % (channelname, fileinfo, text))
    async def send_dm(self, username, text, filename=None):
        if filename is None:
            fileinfo = ""
        else:
            fileinfo = " attached: %s" % filename
        print(linesep + "<DM@%s>%s\n%s" % (username, fileinfo, text))

class MyBackEnd(CLBBackEnd):
    def manage_cmdline(self, cmdline):
        assert isinstance(cmdline, CLBCmdLine)
        parsed = self.parse_cmdline(cmdline.content)
        if parsed is None:
            return []
        cmd = parsed[0]
        name = parsed[1]
        text = "(%s from %s)\n%s" % (cmdline.type, cmdline.author, parsed[2])
        tasks = []
        if cmd == "dm":
            tasks.append(CLBTask(tasktype="dm", username=name, text=text))
        if cmd == "msg":
            tasks.append(CLBTask(tasktype="msg", channelname=name, text=text))
        if cmd == "file":
            tasks.append(CLBTask(tasktype="msg", channelname=name, text=text, filename="dice.png"))
        return tasks
    def parse_cmdline(self, cmdline):
        if not cmdline.startswith("!"):
            return None
        return cmdline[1:].split()
