import imgkit
from pyquery import PyQuery
from typing import List, Tuple, Dict, Any, Optional, cast
import urllib.request
import os
import re
# import yaml
import json


from ..core.clb_data import CLBData
from ..core.clb_error import CLBError


virtual_contest_dir = "virtual_contest"


class AtCoderAPI:
    def __init__(self, data: CLBData) -> None:
        self.data = data
        self.url = "https://kenkoooo.com/atcoder/atcoder-api/info/merged-problems"
        self.json_path = os.path.join(self.data.get_category_dir(virtual_contest_dir),
                                      "problems.json")
        self.problems = None  # type: Optional[List[Dict[str, Any]]]

    def download(self) -> None:
        print("downloading...")
        with urllib.request.urlopen(self.url) as response:
            print("...")
            json_str = response.read().decode("utf-8")
        print("saving...")
        with open(self.json_path, "w", encoding="utf-8") as f:
            f.write(json_str)

    def read(self) -> None:
        if self.problems is not None:
            return
        with open(self.json_path, "r", encoding="utf-8") as f:
            json_str = f.read()
        self.problems = json.loads(json_str)

    def search(self, problem_id: str) -> Dict[str, Any]:
        self.read()
        problems = cast(List[Dict[str, Any]], self.problems)
        for problem in problems:
            if problem["id"] == problem_id:
                return problem
        return {}


class AtCoderProblem:
    def __init__(self, url: str, data: CLBData) -> None:
        self.url = url
        self.data = data
        self.set_id()
        self.set_info()

    def set_id(self) -> None:
        pattern = r"https://beta\.atcoder\.jp/contests/(.*)/tasks/(.*)"
        match_obj = re.match(pattern, self.url)
        if match_obj is None:
            raise CLBError("問題のURLが不正です: %s" % self.url)
        self.contest_id = match_obj.group(1)
        self.problem_id = match_obj.group(2)

    def set_info(self) -> None:
        api = AtCoderAPI(self.data)
        self.info = api.search(self.problem_id)  # type: Dict[str, Any]

    def get_title(self) -> str:
        title = self.info["title"]
        title = re.sub(r"^[A-Z]\.\s*", "", title)
        return title

    def get_id(self) -> str:
        pattern = r"(abc|arc|agc)([0-9]+)_([a-z])"
        match_obj = re.match(pattern, self.problem_id)
        if match_obj is None:
            return self.problem_id
        contest_type = match_obj.group(1)
        contest_count = match_obj.group(2)
        problem_alphabet = match_obj.group(3)
        return "%s %s %s" % (contest_type.upper(), contest_count, problem_alphabet.upper())

    def get_score(self) -> int:
        return int(self.info["point"])


class AtCoderVirtualContest:
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
    import pprint
    data = CLBData()
    # contest_id = "6029001596338176"
    # vc = AtCoderVirtualContest(contest_id, data)
    # # vc.download()
    # problems = vc.get_problems()
    # pprint.pprint(problems)

    # scores = AtCoderScores(data)
    # scores.download()

    # api = AtCoderAPI(data)
    # # api.download()

    # query_list = ["arc076_b", "kupc2015_k", "joisc2011_dragon"]
    # for problem_id in query_list:
    #     print("searching %s..." % problem_id)
    #     pprint.pprint(api.search(problem_id))

    urls = ["https://beta.atcoder.jp/contests/cf17-final-open/tasks/cf17_final_b",
            "https://beta.atcoder.jp/contests/arc076/tasks/arc076_b"]
    for url in urls:
        problem = AtCoderProblem(url, data)
        # pprint.pprint(problem.info)
        print("%s, %s, %s" % (problem.get_id(),
                              problem.get_title(),
                              problem.get_score()))
        print()
