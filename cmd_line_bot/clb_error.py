#!/usr/bin/env python3


class CLBError(Exception):
    def __init__(self, error_msg: str) -> None:
        self.error_msg = error_msg

    def __str__(self) -> str:
        return self.error_msg

    def get_msg_to_discord(self) -> str:
        return "[Error] %s" % self.error_msg


class CLBIndexError(CLBError):
    pass
