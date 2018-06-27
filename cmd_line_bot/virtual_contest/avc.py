import imgkit
from pyquery import PyQuery
from typing import List, Tuple
import urllib.request
import os

from ..core.clb_data import CLBData


class AtCoderVirtualContest:
    # 点数，問題番号などの情報はAtCoderScoresから得るのが良い？
    def __init__(self,
                 contest_id: str,
                 data: CLBData) -> None:
        self.contest_id = contest_id
        self.data = data

    def download(self) -> None:
        url = "https://not-522.appspot.com/contest/" + self.contest_id
        with urllib.request.urlopen(url) as response:
            html = response.read().decode("utf-8")
        html_path = os.path.join(self.data.get_category_dir("virtual_contest"),
                                 self.contest_id+".html")
        png_path = os.path.join(self.data.get_category_dir("virtual_contest"),
                                self.contest_id+".png")
        with open(html_path, "w", encoding="utf-8") as f:
            print("write to %s" % html_path)
            f.write(html)
        print("write to %s" % png_path)
        imgkit.from_string(html, png_path)

    def read(self) -> str:
        # TODO: htmlファイルが存在しないときの処理とか
        html_path = os.path.join(self.data.get_category_dir("virtual_contest"),
                                 self.contest_id+".html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        return html

    def get_problems(self) -> List[Tuple[str, str]]:
        html = self.read()
        query = PyQuery(html)
        result = []
        for a in query("th a"):
            q = PyQuery(a)
            result.append((q.text(), q.attr("href")))
        return result


def avc_test():
    contest_id = "6029001596338176"
    data = CLBData()
    vc = AtCoderVirtualContest(contest_id, data)
    # vc.download()
    problems = vc.get_problems()
    import pprint
    pprint.pprint(problems)
