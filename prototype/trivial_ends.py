#!/usr/bin/env python3
import asyncio
from cmd_line_bot import CLBFrontEnd, CLBBackEnd, CLBTask

class MyFrontEnd(CLBFrontEnd):
    def run(self, callback):
        print("This is MyFrontEnd")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(callback("dm user1 private"))
        loop.run_until_complete(callback("msg ch1 open"))
    async def send_msg(self, channelname, text):
        print("[%s] %s" % (channelname, text))
    async def send_dm(self, username, text):
        print("<DM@%s> %s" % (username, text))

class MyBackEnd(CLBBackEnd):
    def manage_cmdline(self, cmdline):
        # print("backend: " + cmdline)
        parsed = self.parse_cmdline(cmdline)
        if parsed is None:
            return []
        cmd = parsed[0]
        tasks = []
        if cmd == "dm":
            tasks.append(CLBTask(tasktype="dm", username=parsed[1], text=parsed[2]))
        if cmd == "msg":
            tasks.append(CLBTask(tasktype="msg", channelname=parsed[1], text=parsed[2]))
        if cmd == "file":
            tasks.append(CLBTask(tasktype="msg", channelname=parsed[1], text=parsed[2], filename="dice.png"))
        return tasks
    def parse_cmdline(self, cmdline):
        if not cmdline.startswith("!"):
            return None
        return cmdline[1:].split()
