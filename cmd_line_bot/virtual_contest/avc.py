from pprint import pprint
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
            raise CLBError("問題のURLが不正です: {url}".format(url=self.url))
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
        return "{AXC} {count} {alph}".format(AXC=contest_type.upper(),
                                             count=contest_count,
                                             alph=problem_alphabet.upper())

    def get_score(self) -> int:
        if "point" not in self.info.keys():
            return 0
        return int(self.info["point"])


class AtCoderVirtualContest:
    def __init__(self,
                 contest_id: str,
                 data: CLBData) -> None:
        self.contest_id = contest_id
        self.url = "https://not-522.appspot.com/contest/" + self.contest_id
        self.data = data
        self.html_path = os.path.join(self.data.get_category_dir(virtual_contest_dir),
                                      self.contest_id+".html")

    def download(self) -> None:
        with urllib.request.urlopen(self.url) as response:
            html = response.read().decode("utf-8")
        with open(self.html_path, "w", encoding="utf-8") as f:
            print("write to {path}".format(path=self.html_path))
            f.write(html)

    def get_png_file(self) -> str:
        html = self.read()
        png_path = os.path.join(self.data.get_category_dir(virtual_contest_dir),
                                self.contest_id+".png")
        print("write to {path}".format(path=png_path))
        imgkit.from_string(html, png_path)
        return png_path

    def read(self) -> str:
        if not os.path.exists(self.html_path):
            self.download()
        with open(self.html_path, "r", encoding="utf-8") as f:
            html = f.read()
        return html

    def get_title(self) -> str:
        html = self.read()
        query = PyQuery(html)
        title_obj = query("div.container h1.page-header").contents()[0]
        # .contents([0])により，<small class="pull-right">以後のコンテスト情報を切り落としている
        return PyQuery(title_obj).text()

    def get_problems(self) -> List[AtCoderProblem]:
        html = self.read()
        query = PyQuery(html)
        result = []
        for a in query("th a"):
            q = PyQuery(a)
            problem = AtCoderProblem(q.attr("href"), self.data)
            result.append(problem)
        return result

    def get_contest_info(self) -> str:
        title = self.get_title()
        problems = self.get_problems()
        result = title + "\n"
        for problem in problems:
            result += "{score} {id_} {title}\n".format(score=problem.get_score(),
                                                       id_=problem.get_id(),
                                                       title=problem.get_title())
        result += self.url
        return result


def avc_test():
    import pprint
    data = CLBData()
    contest_id = "6029001596338176"
    vc = AtCoderVirtualContest(contest_id, data)
    # vc.download()
    print(vc.get_contest_info())
    # print(vc.get_title())
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

    # urls = ["https://beta.atcoder.jp/contests/cf17-final-open/tasks/cf17_final_b",
    #         "https://beta.atcoder.jp/contests/arc076/tasks/arc076_b"]
    # for url in urls:
    #     problem = AtCoderProblem(url, data)
    #     # pprint.pprint(problem.info)
    #     print("%s, %s, %s" % (problem.get_id(),
    #                           problem.get_title(),
    #                           problem.get_score()))
    #     print()
