#!/usr/bin/env python3
from cmd_line_bot import CmdLineBot
from trivial_ends import MyFrontEnd, MyBackEnd
from discord_frontend import DiscordFrontEnd
from example_backend import example_backend


def main():
    # frontend
    frontend = MyFrontEnd()
    input_frontend = DiscordFrontEnd()
    output_frontend = input_frontend
    # backend
    backend = MyBackEnd()
    backend = example_backend
    # bot
    bot = CmdLineBot(input_frontend, output_frontend, backend)
    bot.run()


if __name__ == '__main__':
    main()
