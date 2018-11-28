from time import sleep
from typing import Callable, Optional  # type annotation でしか使わない

from cmd_line_bot.core.cmd_line_bot import CLBInputFrontEnd, CLBOutputFrontEnd, CLBBackEnd, CLBTask, CmdLineBot
from cmd_line_bot.core.clb_interface import CLBCmdLine, CLBCmdLine_Msg, CLBTask_Msg
# CLBCmdLine は type annotation 内でしか使ってない
from cmd_line_bot.ends.discord_frontend import DiscordFrontEnd


class ExampleInputFrontEnd(CLBInputFrontEnd):
    def run(self, callback: Callable[[CLBCmdLine], None]) -> None:
        print("ExampleInputFrontEnd starts")
        content_list = ["first message", "second message", "third message"]
        for content in content_list:
            cmdline = CLBCmdLine_Msg(content=content,
                                     author="bourbaki",
                                     channelname="my_channel")
            callback(cmdline)   # backend に向けて cmdline を送る
            sleep(0.5)

    def kill(self) -> None:
        pass


class ExampleOutputFrontEnd(CLBOutputFrontEnd):
    def send_msg(self,
                 channelname: str,
                 text: Optional[str],
                 filename: Optional[str]) -> None:
        print("[msg to channel %s]\n%s\n" % (channelname, text))

    def send_dm(self,
                username: str,
                text: Optional[str],
                filename: Optional[str]) -> None:
        print("[dm to user %s]\n%s\n" % (username, text))

    def kill(self) -> None:
        pass


class ExampleBackEnd(CLBBackEnd):
    def manage_cmdline(self,
                       cmdline: CLBCmdLine,
                       send_task: Callable[[CLBTask], None]) -> None:
        text = cmdline.content.replace("message", "msg")
        task = CLBTask_Msg(channelname="general",
                           text=text,
                           cmdline=cmdline)
        send_task(task)         # output frontend に向けて task を送る

    def kill(self) -> None:
        pass


def example2_to_discord():
    discord_frontend = DiscordFrontEnd()
    output_frontend = discord_frontend.output_frontend

    input_frontend = ExampleInputFrontEnd()
    backend = ExampleBackEnd()
    bot = CmdLineBot(input_frontend, output_frontend, backend)
    bot.run()


def example2_from_discord():
    discord_frontend = DiscordFrontEnd()
    input_frontend = discord_frontend.input_frontend

    output_frontend = ExampleOutputFrontEnd()
    backend = ExampleBackEnd()

    bot = CmdLineBot(input_frontend, output_frontend, backend)
    bot.run()


if __name__ == '__main__':
    example2_to_discord()
    # example2_from_discord()
