#!/usr/bin/env python3
from cmd_line_bot.core.cmd_line_bot import CmdLineBot
from cmd_line_bot.core.clb_data import CLBData
from cmd_line_bot.ends.trivial_ends import TrivialInputFrontEnd, TrivialOutputFrontEnd, TrivialBackEnd
from cmd_line_bot.ends.discord_frontend import DiscordFrontEnd
from cmd_line_bot.ends.example_backend import example_backend
from cmd_line_bot.ends.cron_frontend import cron_example
from cmd_line_bot.ends.terminal_frontend import TerminalInputFrontEnd, TerminalOutputFrontEnd


def first_example():
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


def vc_example(test=False):
    from cmd_line_bot.virtual_contest.avc_backend import create_avc_backend
    data = CLBData()
    if not test:
        dfe = DiscordFrontEnd(data=data)
        input_frontend = dfe.input_frontend
        output_frontend = dfe.output_frontend
    else:
        input_frontend = TerminalInputFrontEnd()
        output_frontend = TerminalOutputFrontEnd()
    backend = create_avc_backend(data)
    bot = CmdLineBot([input_frontend], output_frontend, backend)
    bot.run()


if __name__ == '__main__':
    vc_example(test=True)
