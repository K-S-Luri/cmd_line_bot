import os
import sys
import traceback
import tempfile
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter, TerminalFormatter
import imgkit


traceback_dir = "traceback"


def traceback_to_terminal() -> str:
    etype, value, tb = sys.exc_info()
    tbtext = "".join(traceback.format_exception(etype, value, tb))
    lexer = get_lexer_by_name("pytb", stripall=True)
    formatter = TerminalFormatter()
    return highlight(tbtext, lexer, formatter)

def traceback_to_png() -> str:
    etype, value, tb = sys.exc_info()
    tbtext = "".join(traceback.format_exception(etype, value, tb))
    lexer = get_lexer_by_name("pytb", stripall=True)
    formatter = HtmlFormatter(linenos=True, full=True)
    html = highlight(tbtext, lexer, formatter)
    # output_path = os.path.join(tempfile.mkdtemp(),
    #                            datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%N.png"))
    output_path = tempfile.mkstemp(suffix=".png")[1]
    options={"minimum-font-size": 32}
    imgkit.from_string(string=html, output_path=output_path, options=options)
    return output_path
