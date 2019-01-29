import re
from typing import Optional, List, DefaultDict
from datetime import datetime, timedelta
from random import randrange
from collections import defaultdict

from .base import ServerName, User, Problem, Submission, Result
from .vcserver import VCServer


SubmissionDict = DefaultDict[User, DefaultDict[Problem, List[Submission]]]


class ExampleServer(VCServer):
    name: ServerName = ServerName("example")

    def __init__(self):
        super().__init__()
        self.submissions: SubmissionDict = defaultdict(lambda: defaultdict(lambda: []))
        self.count: int = 0     # submission の id とか time をテキトーに生成するために使う

    def update_problems(self) -> None:
        for i, problem in enumerate(self.problems):
            problem_name = "problem_{num}".format(num=i+1)
            problem_score = (i+1) * 100
            problem.set_data(name=problem_name, score=problem_score)

    def update_submissions(self,
                           start: datetime,
                           end: Optional[datetime] = None) -> None:
        for user in self.users:
            i = randrange(len(self.problems))
            problem = self.problems[i]
            # result をランダムに生成
            r = randrange(3)
            if r == 0:
                result = Result.AC
                score = problem.score  # 実際にはサーバーから取得した値を使う
            elif r == 1:
                result = Result.TLE
                score = 0
            else:
                result = Result.WA
                score = 0
            time = datetime(year=2019, month=1, day=1,
                            hour=0, minute=0, second=0)
            time += timedelta(seconds=self.count)
            submission = Submission(problem=problem,
                                    user=user,
                                    result=result,
                                    score=score,
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
