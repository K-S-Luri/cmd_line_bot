from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import List

from .base import ServerName, User, Problem, Submission, VCError, VCDuplicateUserError


class VCServer(metaclass=ABCMeta):
    name: ServerName = ServerName("NONAME")

    @abstractmethod
    def __init__(self,
                 since: datetime,
                 until: datetime) -> None:
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
        self._since: datetime = since
        self._until: datetime = until

    @abstractmethod
    def update_problems(self) -> None:
        "問題の情報(問題名，得点)をサーバーから取ってくる"
        pass

    @abstractmethod
    def update_submissions(self) -> None:
        """submission の一覧をサーバーから取ってくる

self._since と self._until の間の submissions を取得する．
呼び出しごとに，self._since や self._until の値が異なっている可能性があることに注意．
また，キャッシュは考慮されていないので，サブクラスの内部で実装すること．"""
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

    def set_since(self, since: datetime) -> None:
        if self._since < since:
            raise VCError("'since' cannot increase")
        self._since = since

    def set_until(self, until: datetime) -> None:
        if self._until > until:
            raise VCError("'until' cannot decrease")
        self._until = until

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
