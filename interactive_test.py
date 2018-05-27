from lib.debug_util import interactive_test
import asyncio

loop = asyncio.get_event_loop()
# interactive_test()
loop.run_until_complete(interactive_test())
