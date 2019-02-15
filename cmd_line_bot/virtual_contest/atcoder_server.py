import re
from typing import Optional, List, DefaultDict, Tuple, NamedTuple, Any
from datetime import datetime
from collections import defaultdict
import urllib.request
from pyquery import PyQuery as pq

from .base import ServerName, User, Problem, Submission, Result
from .vcserver import VCServer


SubmissionDict = DefaultDict[User, DefaultDict[Problem, List[Submission]]]
WJ_data = NamedTuple("WJ_data", [("url", str), ("user", User), ("problem", Problem), ("submission_number", int)])


class AtCoderServer(VCServer):
    name: ServerName = ServerName("AtCoder")
    DEFAULT_TIME: datetime = datetime(1, 1, 1, 0, 0, 0)
    RESULT_LABELS: List[str] = ["AC", "CE", "MLE", "TLE", "RE", "OLE", "IE", "WA", "WJ", "WR", "NG"]
    RESULT_TYPES: List[Result] = [Result.AC, Result.CE, Result.MLE, Result.TLE, Result.RE, Result.OLE, Result.IE, Result.WA, Result.WJ, Result.WR, Result.NG]

    def __init__(self):
        super().__init__()
        self.submissions: SubmissionDict = defaultdict(lambda: defaultdict(lambda: []))
        self.count: int = 0     # submission の id とか time をテキトーに生成するために使う
        self.submission_urls = []  # 提出画面urlのリスト
        self.time_cache = self.DEFAULT_TIME
        self.table_header_names = []
        self.WJ_list: List[WJ_data] = [] # resultがWJになっている提出のリスト。詳細画面のurl、User、problem、その提出がsubmissions[user][problem]の何番目かを示す数が入る。

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
                if score_str == "":
                    problem_score = 0
                else:
                    problem_score = int(score_str)
                problem.set_data(name=problem_name, score=problem_score)

    def update_submissions(self,
                           start: datetime,
                           end: Optional[datetime] = None) -> None:
        if self.time_cache == self.DEFAULT_TIME:
            self.time_cache = start
        self.WJ_reload()
        self.make_submission_urls()
        now_time = datetime.now()
        for submission_url in self.submission_urls:
            must_check_next_page = True
            page_count = 1
            # 1ページごとにtime_cacheで行われた提出まで見ていく
            while must_check_next_page:
                sub_submission_url = submission_url + "?page=" + str(page_count)
                rows = self.make_page_rows(sub_submission_url)
                for row in rows:
                    row_continue = self.row_process(row, end)
                    if not row_continue:
                        must_check_next_page = False
                        break
                page_count += 1
        self.time_cache = now_time
        if end is not None:
            if self.time_cache > end:
                self.time_cache = end

    def get_submissions(self,
                        user: User,
                        problem: Problem) -> List[Submission]:
        # defaultdict なので存在しないキーにアクセスしても平気
        return self.submissions[user][problem]

    def accept_url(self, url: str) -> bool:
        return bool(re.match(r"https?://atcoder\.jp/contests/", url))

    def WJ_reload(self) -> None:
        """WJ_listに入っているWJの提出を再確認し、ジャッジが決定していたら
          提出のresultを更新する。ここでは通信を行う"""
        new_WJ_list: List[WJ_data] = []
        for WJ in self.WJ_list:
            with urllib.request.urlopen(WJ.url) as response:
                html_str = response.read().decode("utf-8")
                query = pq(html_str)
            # result_queryはchromeでWJ中の提出画面に行ったときのセレクタ、すなわち
            # #main-container > div.row > div:nth-child(2) > div:nth-child(8) > table
            # > tbody > tr:nth-child(7) > td > span
            # とは異なる。なぜかこうでないと正しく取得できない。
            # とりあえず再びWJ(誤答ではない)になるとき、WJ中TLEしてから再びWJ中TLEをみたとき、
            # ACになるとき、CEになるときに動くことは確認できた。
            result_query = query("#main-container > div.row > div:nth-child(2) > div:nth-child(6) > table > tr:nth-child(7) > td > span")
            result_text = result_query.text()
            result = self.determine_result(result_text)
            if result is not Result.WJ:
                self.submissions[WJ.user][WJ.problem][WJ.submission_number].result = result
            else:
                new_WJ_list.append(WJ)
        self.WJ_list = new_WJ_list

    def make_submission_urls(self) -> None:
        """現在登録されている問題をみて、その提出画面のurlの
          リストを作る。2回目以降に呼び出した場合、差分があれば追加する"""
        for problem in self.problems:
            base_url = problem.url
            url_match = re.search("tasks", base_url)
            if url_match is None:
                raise Exception("This can't happen!")
            submission_url = base_url[0:url_match.start()] + "submissions"
            if submission_url not in self.submission_urls:
                self.submission_urls.append(submission_url)

    def make_page_rows(self, sub_submission_url: str) -> Any:
        """提出画面のurlをページごとに指定されたとき、
          そこから提出たちを表す部分を取り出して返す。ここでは通信を行う"""
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
        return rows

    def row_process(self, row: Any, end: Optional[datetime]) -> bool:
        """update_submissionにおいて、1つ1つの提出をpyqueryの形から
          submissionの形になるように処理する。
          そして、提出の時間がtime_cacheより前になっていないか、この先の提出も
          見るべきかどうかを返す"""
        row_contents = dict()
        columns = pq(row)("td")
        for column_name, column in zip(self.table_header_names, columns):
            row_contents[column_name] = pq(column)
        # まず時間を確認する
        row_time_str = row_contents[self.table_header_names[0]].text()
        row_time = datetime.strptime(row_time_str, "%Y-%m-%d %H:%M:%S+0900")
        if end is not None and row_time >= end:
            return True
        if row_time < self.time_cache:
            return False
        # ユーザーを確認する
        user = self.user_check(row_contents)
        if user is None:
            return True
        # 問題を確認する
        problem = self.problem_check(row_contents)
        if problem is None:
            return True
        # idかぶりを確認する
        already_submitted, id_ = self.check_id_duplicated(user, problem, row_contents)
        if already_submitted:
            return True
        # ここまできたらsubmissions行きは確定(WJも登録する?)
        result = self.result_check(user, problem, row_contents)
        # result_text = row_contents[self.table_header_names[6]].text()
        # for label, result_type in zip(self.RESULT_LABELS, self.RESULT_TYPES):
        #     # 必ずどこかでresultが設定される(はず)ので例外処理なし
        #     if result_text == label:
        #         result = result_type
        score_text = row_contents[self.table_header_names[4]].text()
        submission = Submission(problem=problem,
                                user=user,
                                result=result,
                                score=int(score_text),
                                time=row_time,
                                id_=id_)
        # defaultdict なので存在しないキーにアクセスしても平気
        self.submissions[user][problem].append(submission)
        return True

    def user_check(self, row_contents: Any) -> Optional[User]:
        """update_submissionにおいて、与えられた提出が
          コンテスト参加者のものになっているかどうかを確認し、参加者ならそのuserを、
          そうでないならNoneを返す"""
        row_user_text = row_contents[self.table_header_names[2]].text()
        for user in self.users:
            if row_user_text == user.name:
                return user
        return None

    def problem_check(self, row_contents: Any) -> Optional[Problem]:
        """update_submissionにおいて、与えられた提出が
          コンテストの問題の提出になっているかどうかを確認し、コンテスト問題ならその問題を、
          そうでないならNoneを返す
          """
        question_url = row_contents[self.table_header_names[1]]("a").attr("href")  # urlはstr型
        for problem in self.problems:
            problem_url = problem.url
            problem_url_match = re.search(r"/contests", problem_url)
            if problem_url_match is None:
                raise Exception("This can't happen!")
            cut_problem_url = problem_url[problem_url_match.start():]
            if question_url == cut_problem_url:
                # cutした方で比較しているのは、httpとhttpsの差があるかもしれないと思ったから
                return problem
        return None                

    def check_id_duplicated(self, user: User, problem: Problem, row_contents: Any) -> Tuple[bool, str]:
        """update_submissionにおいて、提出のidがかぶっているかどうかと、id_textの内容を返す"""
        # idの取得はジャッジの表示が横に伸びている場合とそうでない場合に分ける
        if row_contents[self.table_header_names[7]].text() == "Detail":
            id_url = row_contents[self.table_header_names[7]]("a").attr("href")
            id_url_match = re.search(r"submissions/", id_url)
            if id_url_match is None:
                raise Exception("This can't happen!")
            id_ = id_url[id_url_match.end():]
        else:
            id_url = row_contents[self.table_header_names[9]]("a").attr("href")
            id_url_match = re.search(r"submissions/", id_url)
            if id_url_match is None:
                raise Exception("This can't happen!")
            id_ = id_url[id_url_match.end():]
        # idかぶりを検証(ページ読み込みの間に1ページ目から2ページ目に提出がずれた場合などにidかぶりが起きうる)
        for old_submission in self.submissions[user][problem]:
            if old_submission.id_ == id_:
                return True, id_
        return False, id_

    def result_check(self, user: User, problem: Problem, row_contents: Any) -> Result:
        """update_submissionにおいて、提出の結果を返す。
          "3/18 WA"などとなっている場合は、処理中としてWJを返すことにする"""
        # ここまできたらsubmissions行きは確定(WJも登録する?)
        result_text = row_contents[self.table_header_names[6]].text()
        result = self.determine_result(result_text)
        if result is Result.WJ:
            # WJのとき、詳細画面のurlを取得し、WJ_listに追加する
            # WJのときはジャッジの表示が横に伸びているはず
            if row_contents[self.table_header_names[7]].text() == "Detail":
                id_url = r"https://atcoder.jp" + row_contents[self.table_header_names[7]]("a").attr("href")
                WJ_submission = WJ_data(id_url, user, problem, len(self.submissions[user][problem]))
                self.WJ_list.append(WJ_submission)
            else:
                raise Exception("This can't happen!")
        return result

    def determine_result(self, result_text: str) -> Result:
        """サイトからとってきた提出結果のテキストから、結果を決定する。
          result_checkおよびWJ_reloadで用いている"""
        result_text_judging_match = re.match(r"\d+/\d+", result_text)
        if result_text_judging_match:
            return Result.WJ
        for label, result_type in zip(self.RESULT_LABELS, self.RESULT_TYPES):
            # 必ずどこかでresultが設定される(はず)ので例外処理なし
            if result_text == label:
                return result_type
        raise Exception("This can't happen!")
