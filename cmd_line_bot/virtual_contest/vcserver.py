from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import List, Optional

from .base import ServerName, User, Problem, Submission, VCError, VCDuplicateUserError


class VCServer(metaclass=ABCMeta):
    name: ServerName = ServerName("NONAME")

    @abstractmethod
    def __init__(self) -> None:
        """__init__ もサブクラスで override する．
特に，submission を保持するコンテナは，サブクラスでメンバとして実装することが期待されている．
コンテナの型は
- List[Submission]
- Dict[User, List[Submission]]
- Dict[Tuple[User, Problem], List[Submission]]
あたりのどれかが良い？
最終的に get_submissions がちゃんと動くのであれば，内部実装は何でも良い"""
        self.users: List[User] = []
        self.problems: List[Problem] = []

    @abstractmethod
    def update_problems(self) -> None:
        "問題の情報(問題名，得点)をサーバーから取ってくる"
        pass

    @abstractmethod
    def update_submissions(self,
                           start: datetime,
                           end: Optional[datetime] = None) -> None:
        """submission の一覧をサーバーから取ってくる

start: バチャコン開始時刻
end: バチャコン終了時刻 (None なら5000兆年後)

start は常に「バチャコン開始時刻」である．取得済みかどうかは関係ない．
なので，キャッシュはサブクラスで実装する．"""
        pass

    @abstractmethod
    def get_submissions(self,
                        user: User,
                        problem: Problem) -> List[Submission]:
        """user の problem での提出の一覧を取得する．

このメソッド内ではサーバーには接続せず，update_submissions で取得済みの情報を参照する．"""
        pass

    @abstractmethod
    def accept_url(self, url: str) -> bool:
        "url がこのサーバーのものかどうかを bool で返す"

    def create_problem(self, url: str) -> Problem:
        "url で与えられる Problem のインスタンスを返す"
        if not self.accept_url(url):
            raise VCError("Invalid url for this server {server_name}".format(server_name=self.name))
        return Problem(url=url, server_name=self.name)

    def add_user(self,
                 user: User,
                 noerror: bool = False) -> None:
        if self.name not in user.ids:
            msg = "Not found: {user_name}'s account in {server_name}"
            raise VCError(msg.format(user_name=user.name,
                                     server_name=self.name))
        if user in self.users:
            if noerror:
                return
            msg = "User {user_name} already added in server {server_name}"
            raise VCDuplicateUserError(msg.format(user_name=user.name,
                                                  server_name=self.name))
        self.users.append(user)

    def add_problem(self, problem: Problem) -> None:
        if problem.server_name != self.name:
            msg = "Invalid problem: problem {url}\n"
            msg += "    is a problem for {server_name_prob}, not {server_name_self}"
            raise VCError(msg.format(url=problem.url,
                                     server_name_prob=problem.server_name,
                                     server_name_self=self.name))
        self.problems.append(problem)
