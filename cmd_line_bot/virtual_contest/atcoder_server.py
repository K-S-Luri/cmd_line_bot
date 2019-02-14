import re
from typing import Optional, List, DefaultDict
from datetime import datetime, timedelta
from collections import defaultdict
import urllib.request
from pyquery import PyQuery as pq

from .base import ServerName, User, Problem, Submission, Result
from .vcserver import VCServer


SubmissionDict = DefaultDict[User, DefaultDict[Problem, List[Submission]]]


class AtCoderServer(VCServer):
    name: ServerName = ServerName("AtCoder")
    DEFAULT_TIME: datetime = datetime(1, 1, 1, 0, 0, 0)

    def __init__(self):
        super().__init__()
        self.submissions: SubmissionDict = defaultdict(lambda: defaultdict(lambda: []))
        self.count: int = 0     # submission の id とか time をテキトーに生成するために使う
        self.submission_urls = []  # 提出画面urlのリスト
        self.time_cache = self.DEFAULT_TIME
        self.table_header_names = []
        self.result_labels = ["AC", "CE", "MLE", "TLE", "RE", "OLE", "IE", "WA", "WJ", "WR", "NG"]
        self.result_types = [Result.AC, Result.CE, Result.MLE, Result.TLE, Result.RE, Result.OLE, Result.IE, Result.WA, Result.WJ, Result.WR, Result.NG]

    def update_problems(self) -> None:
        for problem in self.problems:
            if problem.server_name == self.name:
                with urllib.request.urlopen(problem.url) as response:
                    html_str = response.read().decode("utf-8")
                    query = pq(html_str)
                name_query = query("#main-container > div.row > div:nth-child(2) > span")
                name_str = name_query.text()
                name_match = re.search(r"-\s", name_str)
                if name_match is None:
                    raise Exception("This can't happen!")
                problem_name = name_str[name_match.end():]
                score_query = query("#task-statement > span > span.lang-ja > p > var")
                score_str = score_query.text()
                if score_str is "":
                    problem_score = 0
                else:
                    problem_score = int(score_str)
                problem.set_data(name=problem_name, score=problem_score)

    def update_submissions(self,
                           start: datetime,
                           end: Optional[datetime] = None) -> None:
        if self.time_cache == self.DEFAULT_TIME:
            self.time_cache = start
        for problem in self.problems:
            base_url = problem.url
            url_match = re.search("tasks", base_url)
            if url_match is None:
                raise Exception("This can't happen!")
            submission_url = base_url[0:url_match.start()] + "submissions"
            if submission_url not in self.submission_urls:
                self.submission_urls.append(submission_url)
        now_time = datetime.now()
        for submission_url in self.submission_urls:
            must_check_next_page = True
            page_count = 1
            # 1ページごとにtime_cacheで行われた提出まで見ていく
            while must_check_next_page:
                sub_submission_url = submission_url + "?page=" + str(page_count)
                with urllib.request.urlopen(sub_submission_url) as response:
                    html_str = response.read().decode("utf-8")
                    query = pq(html_str)
                # 表の親を取ってくる
                table = query("#main-container > div.row > div:nth-child(3) > div.panel.panel-default.panel-submission > div.table-responsive > table")
                if self.table_header_names == []:
                    # 表のヘッダ部を取ってくる
                    theads = table("thead > tr > th")
                    # 表のヘッダ部の名前をリストに格納する
                    for thead in theads:
                        thead_text = pq(thead).text()
                        self.table_header_names.append(thead_text)
                # 各行のデータをとってくる
                rows = table("tbody > tr")
                for row in rows:
                    row_contents = dict()
                    columns = pq(row)("td")
                    for column_name, column in zip(self.table_header_names, columns):
                        row_contents[column_name] = pq(column)
                    # まず時間を確認する
                    row_time_str = row_contents[self.table_header_names[0]].text()
                    row_time = datetime.strptime(row_time_str, "%Y-%m-%d %H:%M:%S+0900")
                    if (row_time >= self.time_cache):
                        # ユーザーを確認する
                        row_user_text = row_contents[self.table_header_names[2]].text()
                        for user in self.users:
                            if row_user_text == user.name:
                                # 問題を確認する
                                question_url = row_contents[self.table_header_names[1]]("a").attr("href")  # urlはstr型
                                for problem in self.problems:
                                    problem_url = problem.url
                                    problem_url_match = re.search(r"/contests", problem_url)
                                    if problem_url_match is None:
                                        raise Exception("This can't happen!")
                                    cut_problem_url = problem_url[problem_url_match.start():]
                                    if question_url == cut_problem_url:
                                        # ここまできたらidかぶりじゃない限りsubmissions行きは確定(WJも登録する?)
                                        result_text = row_contents[self.table_header_names[6]].text()
                                        for label, result_type in zip(self.result_labels, self.result_types):
                                            # 必ずどこかでresultが設定される(はず)ので例外処理なし
                                            if result_text == label:
                                                result = result_type
                                        score_text = row_contents[self.table_header_names[4]].text()
                                        # idの取得はジャッジの表示が横に伸びている場合とそうでない場合に分ける
                                        if row_contents[self.table_header_names[7]].text() == "Detail":
                                            id_url = row_contents[self.table_header_names[7]]("a").attr("href")
                                            id_url_match = re.search(r"submissions/", id_url)
                                            if id_url_match is None:
                                                raise Exception("This can't happen!")
                                            id_text = id_url[id_url_match.end():]
                                        else:
                                            id_url = row_contents[self.table_header_names[9]]("a").attr("href")
                                            id_url_match = re.search(r"submissions/", id_url)
                                            if id_url_match is None:
                                                raise Exception("This can't happen!")
                                            id_text = id_url[id_url_match.end():]
                                        # idかぶりを検証(ページ読み込みの間に1ページ目から2ページ目に提出がずれた場合などにidかぶりが起きうる)
                                        already_submitted = False
                                        for old_submission in self.submissions[user][problem]:
                                            if old_submission.id_ == id_text:
                                                already_submitted = True
                                        if not already_submitted:
                                            submission = Submission(problem=problem,
                                                                    user=user,
                                                                    result=result,
                                                                    score=int(score_text),
                                                                    time=row_time,
                                                                    id_=id_text)
                                            # defaultdict なので存在しないキーにアクセスしても平気
                                            self.submissions[user][problem].append(submission)
                                        break
                                break
                    else:
                        must_check_next_page = False
                        break
                page_count += 1
        self.time_cache = now_time

    def get_submissions(self,
                        user: User,
                        problem: Problem) -> List[Submission]:
        # defaultdict なので存在しないキーにアクセスしても平気
        return self.submissions[user][problem]

    def accept_url(self, url: str) -> bool:
        return bool(re.match(r"https?://atcoder\.jp/contests/", url))

    def check_id_duplicated(self, user, problem, row_contents) -> bool:
        # idの取得はジャッジの表示が横に伸びている場合とそうでない場合に分ける
        if row_contents[self.table_header_names[7]].text() == "Detail":
            id_url = row_contents[self.table_header_names[7]]("a").attr("href")
            id_url_match = re.search(r"submissions/", id_url)
            if id_url_match is None:
                raise Exception("This can't happen!")
            id_text = id_url[id_url_match.end():]
        else:
            id_url = row_contents[self.table_header_names[9]]("a").attr("href")
            id_url_match = re.search(r"submissions/", id_url)
            if id_url_match is None:
                raise Exception("This can't happen!")
            id_text = id_url[id_url_match.end():]
        # idかぶりを検証(ページ読み込みの間に1ページ目から2ページ目に提出がずれた場合などにidかぶりが起きうる)
        already_submitted = False
        for old_submission in self.submissions[user][problem]:
            if old_submission.id_ == id_text:
                already_submitted = True
        return already_submitted
