#!/usr/bin/env python3
from cmd_line_bot import CmdLineBot
from discord_frontend import DiscordFrontEnd
from trivial_ends import MyFrontEnd, MyBackEnd

def main():
    token = "NDU1Mjg1OTQwODQ0NDk0ODUw.Df5zIw.Qy0amuaPNJSVSEH30o0H3Gm4e1Y"
    frontend = MyFrontEnd()
    frontend = DiscordFrontEnd(token)
    backend = MyBackEnd()
    clb = CmdLineBot(frontend, backend)
    clb.run()

if __name__ == '__main__':
    main()
