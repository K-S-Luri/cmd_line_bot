#!/usr/bin/env python3
from cmd_line_bot.core.cmd_line_bot import CmdLineBot
from cmd_line_bot.core.clb_interface import CLBCmdLine_Msg
from cmd_line_bot.core.clb_data import CLBData
from cmd_line_bot.ends.trivial_ends import TrivialInputFrontEnd, TrivialOutputFrontEnd, TrivialBackEnd
from cmd_line_bot.ends.discord_frontend import DiscordFrontEnd
from cmd_line_bot.ends.example_backend import example_backend
from cmd_line_bot.ends.cron_frontend import cron_example, CronJob, CronInputFrontEnd
from cmd_line_bot.ends.terminal_frontend import TerminalInputFrontEnd, TerminalOutputFrontEnd
from cmd_line_bot.ends.ipc_frontend import IPCOutputFrontEnd
from cmd_line_bot.path_resolver import check_wkhtmltoimage


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
    # メインのfrontend
    if not test:
        dfe = DiscordFrontEnd(data=data)
        input_frontend = dfe.input_frontend
        output_frontend = dfe.output_frontend
    else:
        # msg_list = ["!show"]
        msg_list = []
        input_frontend = TerminalInputFrontEnd(msg_list=msg_list)
        # output_frontend = TerminalOutputFrontEnd()
        output_frontend = IPCOutputFrontEnd(show_error_image=True)
    # cron frontend
    cmdline = CLBCmdLine_Msg(content="!ac show fromcron",
                             author="vc_bot",
                             channelname="bot")
    job = CronJob(cmdline=cmdline, second=60)
    cron_input_frontend = CronInputFrontEnd([job])
    # backend
    backend = create_avc_backend(data)
    bot = CmdLineBot([input_frontend, cron_input_frontend], output_frontend, backend)
    bot.run()


if __name__ == '__main__':
    check_wkhtmltoimage()
    vc_example(test=False)
