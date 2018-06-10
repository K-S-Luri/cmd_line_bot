#!/usr/bin/env python3
import asyncio
from cmd_line_bot import CLBFrontEnd, CLBBackEnd

class MyFrontEnd(CLBFrontEnd):
    def run(self, callback):
        print("This is MyFrontEnd")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(callback("dm user1 private"))
        loop.run_until_complete(callback("msg ch1 open"))
    async def send_msg(self, channel, text):
        print("[%s] %s" % (channel, text))
    async def send_dm(self, user, text):
        print("<DM@%s> %s" % (user, text))

class MyBackEnd(CLBBackEnd):
    def manage_cmdline(self, cmdline):
        # print("backend: " + cmdline)
        parsed = self.parse_cmdline(cmdline)
        cmd = parsed[0]
        tasks = []
        if cmd == "dm":
            tasks.append({"type": "dm",
                          "user": parsed[1],
                          "text": parsed[2]})
        if cmd == "msg":
            tasks.append({"type": "msg",
                          "channel": parsed[1],
                          "text": parsed[2]})
        return tasks
    def parse_cmdline(self, cmdline):
        return cmdline.split()
