from datetime import datetime, timedelta

from cmd_line_bot.virtual_contest.base import User, Problem
from cmd_line_bot.virtual_contest.example_server import ExampleServer

if __name__ == '__main__':
    since = datetime(year=2019, month=1, day=1, hour=21)
    until = since + timedelta(hours=2)
    server = ExampleServer(since, until)
    server.update_problems
    # user の準備
    user = User(name="Bourbaki")
    user.set_id(server_name=server.name, user_id="bourbaki")
    server.add_user(user)
    # problem の準備
    problem1 = Problem(url="http://example.com/problem_hoge", server_name=server.name)
    server.add_problem(problem1)
    problem2 = Problem(url="http://example.com/problem_fuga", server_name=server.name)
    server.add_problem(problem2)
    # update
    server.update_problems()
    for _ in range(5):
        server.update_submissions()
    for prob in [problem1, problem2]:
        print("[{prob}]".format(prob=prob))
        for submission in server.get_submissions(user, prob):
            print(submission)
