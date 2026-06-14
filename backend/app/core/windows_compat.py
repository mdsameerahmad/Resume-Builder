import sys
import asyncio

if sys.platform == 'win32':
    # Set ProactorEventLoopPolicy for Windows to support subprocesses
    # This must be done before any event loop is created.
    if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
