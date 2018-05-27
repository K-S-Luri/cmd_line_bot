import asyncio
from .config import config
from .util import shuffle
from .cmd import manage_msg, reply_to_msg

# Dummy classes
class DummyClient:
    async def send_message(self, to, text):
        output = "<@%s>" % to
        if "\n" not in text:
            output += " " + text
        else:
            if not text.endswith("\n"):
                text += "\n"
            output += "\n" + text
        print(output)
    async def send_file(self, to, filename):
        print("<@%s> send %s" % (to, filename))
class DummyMessage:
    def __init__(self, content, author):
        self.author = DummyAuthor(author)
        self.channel = DummyAuthor(author)
        self.server = DummyServer()
        self.content = content
class DummyServer:
    def __init__(self):
        member_names = ["hoge", "fuga", "piyo"]
        self.members = list(map(lambda name: DummyMember(name),
                                member_names))
        self.name = "dummyserver"
    def get_member_named(self, name):
        return name
    def __str__(self):
        return self.name
class DummyMember:
    def __init__(self, name):
        self.name = name
class DummyAuthor:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name

loop = asyncio.get_event_loop()
async def emulate_message(msg, author="DummyAuthor", msg_id=0):
    if not isinstance(msg, str):
        raise Exception("msgはstrで入力して")
    print("\n%s---[%s]---" % (msg_id, msg))
    dmsg = DummyMessage(msg, author)
    global loop
    try:
        await manage_msg(dmsg)
        return True
    except Exception:
        import traceback
        print(traceback.format_exc())
        return None


config.load()
config.set_client(DummyClient())
config.set_server(DummyServer())
client = config.get_client()
loop.run_until_complete(config.send_data_to_client())
