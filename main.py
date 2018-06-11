#!/usr/bin/env python3
from cmd_line_bot import CmdLineBot
from trivial_ends import MyFrontEnd, MyBackEnd
from discord_frontend import DiscordFrontEnd
from example_backend import example_backend


def main():
    token = "NDU1Mjg1OTQwODQ0NDk0ODUw.Df5zIw.Qy0amuaPNJSVSEH30o0H3Gm4e1Y"
    # frontend
    frontend = MyFrontEnd()
    frontend = DiscordFrontEnd(token)
    # backend
    backend = MyBackEnd()
    backend = example_backend
    # bot
    bot = CmdLineBot(frontend, backend)
    bot.run()

if __name__ == '__main__':
    main()
