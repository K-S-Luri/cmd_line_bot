from typing import List

from .vcserver import VCServer
from .base import Result, User, Problem, Submission, VCDuplicateUserError


class VirtualContest:
    def __init__(self, servers: List[VCServer]):
        self.servers: List[VCServer] = servers
        self.users: List[User] = []
        self.problems: List[Problem] = []

    def add_user(self,
                 user: User,
                 noerror: bool = False) -> None:
        for server in self.servers:
            server.add_user(user, noerror)
        if user in self.users:
            if noerror:
                return
            msg = "User {user_name} already added in the virtual contest"
            raise VCDuplicateUserError(msg.format(user_name=user.name))
        self.users.append(user)

    def add_problem(self, problem: Problem) -> None:
        pass

    def update_problems(self) -> None:
        pass

    def update_submissions(self) -> None:
        pass
