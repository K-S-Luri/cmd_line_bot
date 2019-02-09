import pip
import sys
from setuptools import setup
from pkg_resources import parse_version


if parse_version(pip.__version__) < parse_version("18.0"):
    print("[ERROR] Update pip: pip install -U pip", file=sys.stderr)
    sys.exit(1)


setup(
    name="cmd_line_bot",
    version="1.0",
    install_requires=[
        "discord.py@git+https://github.com/Rapptz/discord.py@async",
        "pytypes",
        "pyyaml",
        "imgkit",
        "pyquery",
        "pygments",
        "websockets>=6.0",      # for 3.7
        "aiohttp>=3.5",         # for 3.7
    ],
    packages=["cmd_line_bot"]
)
