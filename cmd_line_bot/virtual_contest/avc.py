import imgkit
from pyquery import PyQuery
from typing import List, Tuple
import urllib.request
import os

from ..core.clb_data import CLBData


def download_avc(contest_id: str,
                 data: CLBData) -> None:
    url = "https://not-522.appspot.com/contest/" + contest_id
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
    html_path = os.path.join(data.get_category_dir("virtual_contest"),
                             contest_id+".html")
    png_path = os.path.join(data.get_category_dir("virtual_contest"),
                            contest_id+".png")
    with open(html_path, "w", encoding="utf-8") as f:
        print("write to %s" % html_path)
        f.write(html)
    print("write to %s" % png_path)
    imgkit.from_string(html, png_path)


def read_avc(contest_id: str,
             data: CLBData) -> str:
    html_path = os.path.join(data.get_category_dir("virtual_contest"),
                             contest_id+".html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    return html


def get_problems(contest_id: str,
                 data: CLBData) -> List[Tuple[str, str]]:
    html = read_avc(contest_id, data)
    query = PyQuery(html)
    result = []
    for a in query("th a"):
        q = PyQuery(a)
        result.append((q.text(), q.attr("href")))
    return result


def avc_test():
    contest_id = "6029001596338176"
    data = CLBData()
    # download_avc(contest_id, data)
    problems = get_problems(contest_id, data)
    import pprint
    pprint.pprint(problems)
