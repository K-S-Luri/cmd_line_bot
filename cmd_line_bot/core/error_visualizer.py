from typing import Optional
import os
import sys
import traceback
import tempfile
try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter, TerminalFormatter
except ImportError:
    print("WARNING: failed to import module 'pygments'")
try:
    import imgkit
except ImportError:
    print("WARNING: failed to import module 'imgkit'")
try:
    # Convert ANSI escape character sequences for Windows
    import colorama
    colorama.init()
except ImportError:
    if os.name == "nt":
        print("WARNING: failed to import module 'colorama'")

traceback_dir = "traceback"


def get_traceback() -> str:
    etype, value, tb = sys.exc_info()
    tbtext = "".join(traceback.format_exception(etype, value, tb))
    return tbtext


def get_traceback_for_terminal() -> str:
    tbtext = get_traceback()
    if "pygments" not in sys.modules:
        return tbtext
    lexer = get_lexer_by_name("pytb", stripall=True)
    formatter = TerminalFormatter()
    return highlight(tbtext, lexer, formatter)


def save_traceback_as_jpg() -> Optional[str]:
    if ("pygments" not in sys.modules) or ("imgkit" not in sys.modules):
        return None
    tbtext = get_traceback()
    lexer = get_lexer_by_name("pytb", stripall=True)
    formatter = HtmlFormatter(linenos=True, full=True)
    html = highlight(tbtext, lexer, formatter)
    output_path = tempfile.mkstemp(suffix=".jpg")[1]
    options={"minimum-font-size": 32}
    imgkit.from_string(string=html, output_path=output_path, options=options)
    return output_path
