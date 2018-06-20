#!/usr/bin/env python3
from cmd_line_bot import CLBInputFrontEnd
from clb_interface import CLBCmdLine, CLBCmdLine_Msg
from typing import List
from datetime import datetime
from time import sleep


class CronJob:
    def __init__(self,
                 cmdline: CLBCmdLine,
                 second: int) -> None:
        self.cmdline = cmdline
        self.second = second


class CronInputFrontEnd(CLBInputFrontEnd):
    def __init__(self, jobs: List[CronJob]) -> None:
        self.jobs = jobs
        self._kill = False
        self.job_counts = [0] * len(self.jobs)

    def run(self, callback):
        start_time = datetime.now()
        while not self._kill:
            time = (datetime.now() - start_time).total_seconds()
            for i in range(len(self.jobs)):
                job = self.jobs[i]
                if time > job.second * self.job_counts[i]:
                    cmdline = job.cmdline
                    callback(cmdline)
                    self.job_counts[i] += 1
            sleep(1)

    def kill(self):
        self._kill = True


def cron_example() -> CronInputFrontEnd:
    cmdline = CLBCmdLine_Msg(content="!time",
                             author="wktkshn",
                             channelname="general")
    job = CronJob(cmdline=cmdline, second=10)
    return CronInputFrontEnd([job])
