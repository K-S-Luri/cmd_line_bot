from sjlib.dummy import emulate_message
from sjlib.debug_util import make_symlink_to_latest
from sjlib.sjutil import add_wkhtmltoimage_to_path, add_xvfb_to_path
import os, sys
import asyncio

# Windowsでのpathの設定
if os.name == "nt":
    add_wkhtmltoimage_to_path()
    add_xvfb_to_path()

# messages = ["!p w h r a",
#             "!o t w",
#             "!config rate 3",
#             "!s", "!ra", "!r",
#             # "!s", "!ra", "!k 13","!r",
#             # # "!s", "!deleteresult", "!s",
#             # "!score",
#             # # "!config load score_double",
#             # "!config rate 2",
#             # "!s", "!ra", "!r",
#             "!score"]

messages = ["!p w h r a",
            "!o t w",
            "!config load score_normal",
            "!s", "!ra", "!r",
            "!config load score_nobonus",
            "!s", "!ra", "!r",
            "!config load score_with_nokill",
            "!s", "!ra", "!r",
            # "!s", "!ra", "!r",
            # "!bonus nokill 1",
            # "!bonus hoge 12",
            "!score",
            "!config rate 3",
            "!s", "!ra", "!r",
            "!score"]

loop = asyncio.get_event_loop()
errors = []
for i in range(len(messages)):
    msg = messages[i]
    msg_status = loop.run_until_complete(emulate_message(msg, msg_id=i))
    if msg_status is False:
        errors.append(("SJError", i, msg))
    elif msg_status is None:
        errors.append(("FatalError", i, msg))

print()
make_symlink_to_latest()

if len(errors) == 0:
    sys.exit(0)
else:
    print("\n\n=====<<< ERRORS >>>=====")
    for e in errors:
        print(e)
    sys.exit(1)
