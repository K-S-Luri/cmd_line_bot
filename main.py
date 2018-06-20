#!/usr/bin/env python3
from cmd_line_bot import CmdLineBot
from trivial_ends import TrivialInputFrontEnd, TrivialOutputFrontEnd, TrivialBackEnd
from discord_frontend import DiscordFrontEnd
from example_backend import example_backend


def main():
    # frontend
    input_frontend, output_frontend = TrivialInputFrontEnd(), TrivialOutputFrontEnd()
    d = DiscordFrontEnd()
    # input_frontend = d.input_frontend
    output_frontend = d.output_frontend
    # backend
    backend = TrivialBackEnd()
    backend = example_backend
    # bot
    bot = CmdLineBot(input_frontend, output_frontend, backend)
    bot.run()


if __name__ == '__main__':
    main()
