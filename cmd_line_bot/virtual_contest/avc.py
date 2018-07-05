from pprint import pprint
import imgkit
from pyquery import PyQuery
from typing import List, Tuple, Dict, Any, Optional, cast, Match, Union
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


def parse_score_td(td: PyQuery) -> Dict[str, Union[int, str]]:
    result = {"score": 0,
              "WA": 0,
              "time": "?",
              "status": "?"}  # type: Dict[str, Union[int, str]]
    for span in td("span").items():
        style = span.attr("style")
        if style == "color: #00AA3E; font-weight: bold;":
            score = int(span.text())
            result["score"] = score
            if score > 0:
                result["status"] = "AC"
            else:
                result["status"] = "NG"
        elif style == "color: #00F; font-weight: bold;":
            result["score"] = int(span.text())
            result["status"] = "TOTAL"
        elif style == "color: #F00;":
            match_obj = re.match(r"\(([0-9]+)\)", span.text())
            match_obj = cast(Match[Any], match_obj)
            WA_count = match_obj.group(1)
            result["WA"] = WA_count
        elif (style is None) and (td.text() == "-"):
            result["status"] = "NO_SUBMISSION"
        elif (style is None):
            match_obj = re.match(r"\[([0-9]+):([0-9]+)\]", span.text())
            match_obj = cast(Match[Any], match_obj)
            minute = int(match_obj.group(1))
            second = int(match_obj.group(2))
            time_str = "[{minute:02d}:{second:02d}]".format(minute=minute, second=second)
            result["time"] = time_str
    return result


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

    def get_status_list(self) -> List[Dict[str, Any]]:
        html = self.read()
        num_problems = len(self.get_problems())
        status_list = []
        query = PyQuery(html)
        for tr in query("tbody tr").items():
            username_th = tr("th:nth-child(2)")
            username = username_th.text()
            results = []
            user_status = {"username": username}
            items = list(tr("td").items())
            for i in range(num_problems):
                results.append(parse_score_td(items[i]))
            user_status["results"] = results
            user_status["total"] = parse_score_td(items[-1])
            status_list.append(user_status)
        return status_list

    def get_AC_dict(self) -> Dict[str, List[int]]:
        status_list = self.get_status_list()
        AC_dict = {}  # type: Dict[str, List[int]]
        for status in status_list:
            username = status["username"]
            user_AC_list = []
            results = status["results"]
            for i in range(len(results)):
                problem = results[i]
                if problem["status"] == "AC":
                    user_AC_list.append(i)
            AC_dict[username] = user_AC_list
        return AC_dict

    def get_new_AC_list(self,
                        old_virtual_contest: Any) -> List[Tuple[str, int]]:
        # old_virtual_contest: AtCoderVirtualContest にすると undefinedと言われる…
        current_AC_dict = self.get_AC_dict()
        old_AC_dict = old_virtual_contest.get_AC_dict()
        new_AC_list = []
        for username, AC_list in current_AC_dict.items():
            for problem_number in AC_list:
                if problem_number not in old_AC_dict[username]:
                    new_AC_list.append((username, problem_number))
        return new_AC_list


def avc_test():
    data = CLBData()
    contest_id = "6029001596338176"
    vc = AtCoderVirtualContest(contest_id, data)
    vc.download()
    print(vc.get_contest_info())
    # print(vc.get_title())
    # problems = vc.get_problems()
    # pprint.pprint(problems)

    pprint(vc.get_status_list())
    pprint(vc.get_AC_dict())

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
