import imgkit
from pyquery import PyQuery
from typing import List, Tuple, Dict, Any, Optional, cast
import urllib.request
import os
import yaml

from ..core.clb_data import CLBData


virtual_contest_dir = "virtual_contest"


class AtCoderScores:
    def __init__(self, data: CLBData) -> None:
        self.url = "https://atcoder-scores.herokuapp.com/index.html"
        self.data = data
        self.html_path = os.path.join(self.data.get_category_dir(virtual_contest_dir),
                                      "scores.html")

    def download(self) -> None:
        with urllib.request.urlopen(self.url) as response:
            html = response.read().decode("utf-8")
        with open(self.html_path, "w", encoding="utf-8") as f:
            f.write(html)

    def read(self) -> str:
        with open(self.html_path, "r", encoding="utf-8") as f:
            html = f.read()
        return html


class AtCoderAPI:
    def __init__(self, data: CLBData) -> None:
        self.data = data
        self.url = "https://kenkoooo.com/atcoder/atcoder-api/info/merged-problems"
        self.yaml_path = os.path.join(self.data.get_category_dir(virtual_contest_dir),
                                      "problems.yaml")
        self.problems = None  # type: Optional[List[Dict[str, Any]]]

    def download(self) -> None:
        print("downloading...")
        with urllib.request.urlopen(self.url) as response:
            print("...")
            yaml_str = response.read().decode("utf-8")
        print("loading yaml...")
        yaml_data = yaml.load(yaml_str)
        self.problems = yaml_data
        print("dumping yaml...")
        yaml_str = yaml.dump(yaml_data)
        print("saving...")
        with open(self.yaml_path, "w", encoding="utf-8") as f:
            f.write(yaml_str)

    def read(self) -> None:
        if self.problems is not None:
            return
        with open(self.yaml_path, "r", encoding="utf-8") as f:
            yaml_str = f.read()
        print("loading yaml...")
        self.problems = yaml.load(yaml_str)
        print("ok")

    def search(self, problem_id: str) -> Dict[str, Any]:
        self.read()
        problems = cast(List[Dict[str, Any]], self.problems)
        for problem in problems:
            if problem["id"] == problem_id:
                return problem
        return {}


class AtCoderVirtualContest:
    # 点数，問題番号などの情報はAtCoderScoresから得るのが良い？
    def __init__(self,
                 contest_id: str,
                 data: CLBData) -> None:
        self.contest_id = contest_id
        self.data = data
        self.html_path = os.path.join(self.data.get_category_dir(virtual_contest_dir),
                                      self.contest_id+".html")

    def download(self) -> None:
        url = "https://not-522.appspot.com/contest/" + self.contest_id
        with urllib.request.urlopen(url) as response:
            html = response.read().decode("utf-8")
        png_path = os.path.join(self.data.get_category_dir(virtual_contest_dir),
                                self.contest_id+".png")
        with open(self.html_path, "w", encoding="utf-8") as f:
            print("write to %s" % self.html_path)
            f.write(html)
        print("write to %s" % png_path)
        imgkit.from_string(html, png_path)

    def read(self) -> str:
        # TODO: htmlファイルが存在しないときの処理とか
        with open(self.html_path, "r", encoding="utf-8") as f:
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

    # scores = AtCoderScores(data)
    # scores.download()

    api = AtCoderAPI(data)
    # api.download()

    query_list = ["arc076_b", "kupc2015_k", "joisc2011_dragon"]
    for problem_id in query_list:
        print("searching %s..." % problem_id)
        pprint.pprint(api.search(problem_id))
