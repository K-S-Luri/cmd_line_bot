from datetime import datetime

from cmd_line_bot.virtual_contest.base import User, Problem
from cmd_line_bot.virtual_contest.example_server import ExampleServer

if __name__ == '__main__':
    server = ExampleServer()
    server.update_problems
    user = User(name="Bourbaki")
    problem = Problem(url="http://example.com", server_name=server.name)
    server.add_user(user)
    server.add_problem(problem)
    for _ in range(10):
        server.update_submissions(datetime.now())
    print(server.get_submissions(user, problem))
