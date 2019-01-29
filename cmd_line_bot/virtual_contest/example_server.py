import re
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from random import randrange
from collections import defaultdict


from .base import ServerName, User, Problem, Submission, Result
from .vcserver import VCServer


class ExampleServer(VCServer):
    name: ServerName = ServerName("example_server")

    def __init__(self):
        super().__init__()
        self.submissions: Dict[User, Dict[Problem, List[Submission]]] = {}
        self.count: int = 0

    def update_problems(self) -> None:
        for problem in self.problems:
            pass

    def update_submissions(self,
                           start: datetime,
                           end: Optional[datetime] = None) -> None:
        for user in self.users:
            if user not in self.submissions:
                self.submissions[user] = {}
            for problem in self.problems:
                self.submissions[user][problem] = []
        for user in self.users:
            i = randrange(len(self.problems))
            problem = self.problems[i]
            result = Result.AC
            time = datetime(year=2019, month=1, day=1,
                            hour=0, minute=0, second=0)
            time += timedelta(seconds=self.count)
            submission = Submission(problem=problem,
                                    user=user,
                                    result=result,
                                    score=100,
                                    time=time,
                                    id_=str(self.count))
            self.submissions[user][problem].append(submission)
            self.count += 1

    def get_submissions(self,
                        user: User,
                        problem: Problem) -> List[Submission]:
        return self.submissions[user][problem]

    def accept_url(self, url: str) -> bool:
        return bool(re.match(r"https?://example\.com/", url))
