from abc import ABCMeta, abstractmethod
import datetime
from typing import List
from .base import ServerName, Result, User, Problem, Submission


class VCServer(metaclass=ABCMeta):
    name: ServerName = ServerName("NONAME")

    @abstractmethod
    def update_problems(self) -> None:
        "問題の情報(問題名，得点)をサーバーから取ってくる"
        pass

    @abstractmethod
    def update_submissions(self,
                           start: datetime.datetime,
                           end: datetime.datetime = None) -> None:
        """submission の一覧をサーバーから取ってくる

start: バチャコン開始時刻
end: バチャコン終了時刻

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
