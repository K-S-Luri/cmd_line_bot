from datetime import datetime

from cmd_line_bot.virtual_contest.base import User, Problem
from cmd_line_bot.virtual_contest.example_server import ExampleServer

if __name__ == '__main__':
    server = ExampleServer()
    server.update_problems
    # user の準備
    user = User(name="Bourbaki")
    user.set_id(server_name=server.name, user_id="bourbaki")
    server.add_user(user)
    # problem の準備
    problem = Problem(url="http://example.com/problem_hoge", server_name=server.name)
    server.add_problem(problem)
    # update
    server.update_problems()
    for _ in range(10):
        server.update_submissions(datetime.now())
    print(server.get_submissions(user, problem))
