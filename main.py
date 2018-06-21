#!/usr/bin/env python3
from cmd_line_bot.cmd_line_bot import CmdLineBot
from cmd_line_bot.trivial_ends import TrivialInputFrontEnd, TrivialOutputFrontEnd, TrivialBackEnd
from cmd_line_bot.discord_frontend import DiscordFrontEnd
from cmd_line_bot.example_backend import example_backend
from cmd_line_bot.cron_frontend import cron_example


def main():
    # frontend
    input_frontend, output_frontend = TrivialInputFrontEnd(), TrivialOutputFrontEnd()
    d = DiscordFrontEnd()
    input_frontend = d.input_frontend
    output_frontend = d.output_frontend
    # cron frontend
    cron_input_frontend = cron_example()
    # backend
    backend = TrivialBackEnd()
    backend = example_backend
    # bot
    bot = CmdLineBot([input_frontend, cron_input_frontend], output_frontend, backend)
    bot.run()


if __name__ == '__main__':
    main()
