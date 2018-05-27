from .config import config
import os
from .dummy import emulate_message

async def interactive_test():
    while True:
        input_line = input(">> ")
        await emulate_message(input_line)
