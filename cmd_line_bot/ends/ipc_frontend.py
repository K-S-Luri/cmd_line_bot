from typing import List, Optional
import socket
import os
import shutil

from ..core.cmd_line_bot import CLBInputFrontEnd, CLBOutputFrontEnd
from ..core.clb_interface import CLBCmdLine_Msg, CLBCmdLine_DM
from .ipc_server import get_port

linesep = "----------\n"

class IPCOutputFrontEnd(CLBOutputFrontEnd):
    def __init__(self,
                 port: Optional[int] = None,
                 show_error_image: bool = True) -> None:
        self.host = "localhost"
        if port is None:
            self.port = get_port()
        else:
            self.port = port
        self.show_error_image = show_error_image
        send_success = self._send_to_server("Connection from IPCOutputFrontEnd")
        if not send_success:
            print("You should consider to run `python ipc_server.py` in another terminal")

    def send_msg(self, channelname, text, filename=None):
        destination_str = "[%s]" % channelname
        self._send_msg_or_dm(destination_str, text, filename)

    def send_dm(self, username, text, filename=None):
        destination_str = "<DM@%s>" % username
        self._send_msg_or_dm(destination_str, text, filename)

    def _send_msg_or_dm(self,
                        destination_str: str,
                        text: str,
                        filename: Optional[str]) -> None:
        if filename is None:
            fileinfo = ""
        else:
            fileinfo = " attached: {filename}".format(filename=filename)
            if self.show_error_image and shutil.which("xdg-open"):
                os.system("xdg-open {filename} &".format(filename=filename))
        msg_to_server = linesep + "{destination}{fileinfo}\n{text}".format(
            destination=destination_str,
            fileinfo=fileinfo,
            text=text)
        send_success = self._send_to_server(msg_to_server)
        if not send_success:
            print(msg_to_server)

    def _send_to_server(self, msg: str) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((self.host, self.port))
            except ConnectionRefusedError:
                print("Server is not running on %s:%s" % (self.host, self.port))
                return False
            sock.sendall(msg.encode("utf-8"))
            sock.recv(1024)     # サーバーからのメッセージを受信．これいる？
            return True

    def kill(self):
        pass
