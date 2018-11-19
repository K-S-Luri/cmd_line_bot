import sys
import traceback
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter, TerminalFormatter


def traceback_to_terminal() -> str:
    etype, value, tb = sys.exc_info()
    tbtext = "".join(traceback.format_exception(etype, value, tb))
    lexer = get_lexer_by_name("pytb", stripall=True)
    formatter = TerminalFormatter()
    return highlight(tbtext, lexer, formatter)
