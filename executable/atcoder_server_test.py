from datetime import datetime, timedelta
from time import sleep

from cmd_line_bot.virtual_contest.base import User, Problem
from cmd_line_bot.virtual_contest.atcoder_server import AtCoderServer

if __name__ == '__main__':
    server = AtCoderServer(datetime.now() - timedelta(hours=2), datetime.now() - timedelta(hours=1))
    server.update_problems
    # user の準備
    user = User(name="Ruki")
    user.set_id(server_name=server.name, user_id="Ruki")
    server.add_user(user)
    user2 = User(name="Prichino")
    user2.set_id(server_name=server.name, user_id="Prichino")
    server.add_user(user2)
    # problem の準備
    problem1 = Problem(url="https://atcoder.jp/contests/abc120/tasks/abc120_b", server_name=server.name)
    server.add_problem(problem1)
    problem2 = Problem(url="https://atcoder.jp/contests/abc120/tasks/abc120_d", server_name=server.name)
    server.add_problem(problem2)
    # update
    server.update_problems()
    # 提出を受け取る
    server.update_submissions()
    for prob in [problem1, problem2]:
        print("[{prob}]".format(prob=prob))
        for submission in server.get_submissions(user, prob):
            print(submission)
        for submission in server.get_submissions(user2, prob):
            print(submission)
    sleep(5)
    print("reload")
    server.set_until(datetime.now())
    server.update_submissions()
    for prob in [problem1, problem2]:
        print("[{prob}]".format(prob=prob))
        for submission in server.get_submissions(user, prob):
            print(submission)
        for submission in server.get_submissions(user2, prob):
            print(submission)
    sleep(5)
    print("reload")
    server.set_since(datetime.now() - timedelta(hours=3))
    server.update_submissions()
    for prob in [problem1, problem2]:
        print("[{prob}]".format(prob=prob))
        for submission in server.get_submissions(user, prob):
            print(submission)
        for submission in server.get_submissions(user2, prob):
            print(submission)
