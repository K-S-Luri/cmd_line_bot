from datetime import datetime, timedelta

from cmd_line_bot.virtual_contest.base import User, Problem
from cmd_line_bot.virtual_contest.atcoder_server import AtCoderServer

if __name__ == '__main__':
    server = AtCoderServer()
    server.update_problems
    # user の準備
    user = User(name="asaka")
    user.set_id(server_name=server.name, user_id="asaka")
    server.add_user(user)
    user2 = User(name="zekatsu")
    user2.set_id(server_name=server.name, user_id="zekatsu")
    server.add_user(user2)
    # problem の準備
    problem1 = Problem(url="https://atcoder.jp/contests/abc117/tasks/abc117_b", server_name=server.name)
    server.add_problem(problem1)
    problem2 = Problem(url="https://atcoder.jp/contests/abc117/tasks/abc117_d", server_name=server.name)
    server.add_problem(problem2)
    # update
    server.update_problems()
    for _ in range(5):
        server.update_submissions(datetime.now() - timedelta(hours=2))
        server.update_submissions(datetime.now())
    for prob in [problem1, problem2]:
        print("[{prob}]".format(prob=prob))
        for submission in server.get_submissions(user, prob):
            print(submission)
        for submission in server.get_submissions(user2, prob):
            print(submission)
