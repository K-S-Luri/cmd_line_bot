from typing import NewType, Dict
from enum import Enum, auto
import datetime


ServerName = NewType("ServerName", str)


class VCError(Exception):
    "virtual_contest 内で発生した，想定範囲内のエラー"


class VCDuplicateUserError(VCError):
    "User を重複して登録しようとしたときに送出するエラー"


class Result(Enum):
    "回答結果．とりあえず AtCoder に準拠しているけど，必要があれば他のサイトのものも加える"
    AC = auto()   # Accepted
    CE = auto()   # Compilation Error
    MLE = auto()  # Memory Limit Exceeded
    TLE = auto()  # Time Limit Exceeded
    RE = auto()   # Runtime Error
    OLE = auto()  # Output Limit Exceeded
    IE = auto()   # Internal Error
    WA = auto()   # Wrong Answer
    WJ = auto()   # Waiting for Judge
    WR = auto()   # Waiting for Re-judging
    NG = auto()   # AtCoder の内部エラー？ IE との違いは謎
    # NotSet = auto()  # サーバーからの情報を得る前にとりあえず入れる値(不要？)


class User:
    "ユーザーを表すクラス．一人のユーザーが複数のサイトにアカウントを持っている(かもしれない)想定"
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.ids: Dict[ServerName, str] = {}  # {"atcoder": "hoge", "aoj": "hoge1234"}

    def set_id(self, server_name: ServerName, user_id: str) -> None:
        self.ids[server_name] = user_id


class Problem:
    def __init__(self,
                 url: str,
                 server_name: ServerName) -> None:
        self.url: str = url     # 問題のURL(例: "https://atcoder.jp/contests/practice/tasks/practice_1")
        self.server_name: ServerName = server_name
        self.name: str = "NONAME"  # 問題名(例: 「はじめてのあっとこーだー」)
        self.score: int = 0     # 実際のスコア計算には使わず，summaryの表示(？)のみに使う

    def set_data(self, name: str, score: int):
        self.name = name
        self.score = score


class Submission:
    def __init__(self,
                 problem: Problem,
                 user: User,
                 result: Result,
                 score: int,
                 time: datetime.datetime,
                 id_: str) -> None:
        self.problem: Problem = problem
        self.user: User = user
        self.result: Result = result
        self.score: int = score  # 部分点とかマラソンに対応するために，各 Submission ごとに score を保持
        self.time: datetime.datetime = time  # 提出日時
        self.id_: str = id_     # 一意な識別子．重複取得の確認とかに使う

    def __eq__(self, other) -> bool:
        "同値性は id_ だけで判定する．たくさんの assert 文は不正なデータの検出のため"
        if self.id_ != other.id_:
            return False
        assert self.problem == other.problem
        assert self.user == other.user
        assert self.result == other.result
        assert self.score == other.score
        assert self.time == other.time
        return True


if __name__ == '__main__':
    hoge = User(name="hoge")
    fuga = User(name="fuga")
    print(hoge == fuga)
    prob = Problem(url="https://atcoder.jp/...", server_name=ServerName("atcoder"))
    prob2 = Problem(url="https://atcoder.jp/...", server_name=ServerName("atcoder"))
    print("prob", prob == prob2)
    time = datetime.datetime.now()
    subm = Submission(problem=prob,
                      user=hoge,
                      result=Result.AC,
                      score=100,
                      time=time,
                      id_="123456")
