from typing import List, Union, cast
import re

from .avc import AtCoderVirtualContest, AtCoderAPI
from ..core.clb_interface import CLBTask, CLBTask_Msg, CLBTask_DM, create_reply_task
from ..core.clb_error import CLBError
from ..core.clb_data import CLBData
from ..ends.cmd_arg_backend import CmdArgBackEnd, CLBCmd, CLBCmdWithSub, CLBCmdArgLine


avc_category = "virtual_contest"


class RootCmd(CLBCmdWithSub):
    def __init__(self, data):
        self._documentation = "root command"
        self._subcmds = [Cmd_Show(data),
                         Cmd_Set(data),
                         Cmd_Img(data),
                         Cmd_Download(data)]


class Cmd_Show(CLBCmd):
    def __init__(self, data):
        self._keys = ["show"]
        self._documentation = "showする"
        self._data = data

    def run(self, cmdargline, pointer):
        contest_id = self._data.get_data(avc_category, "contest_id")
        if contest_id is None:
            raise CLBError("contest_idをsetしてください")
        vc = AtCoderVirtualContest(contest_id, self._data)
        vc_info = vc.get_contest_info()
        print(vc_info)
        tasks = [create_reply_task(cmdargline.cmdline, vc_info)]
        return tasks


class Cmd_Set(CLBCmd):
    def __init__(self, data: CLBData) -> None:
        self._keys = ["set"]
        self._documentation = "setする"
        self._data = data

    def run(self,
            cmdargline: CLBCmdArgLine,
            pointer: int) -> List[Union[CLBTask, List[CLBTask]]]:
        if cmdargline.get_num_args(pointer) < 1:
            raise CLBError("引数が足りません")
        elif cmdargline.get_num_args(pointer) > 1:
            raise CLBError("引数が多すぎます")
        contest_id_raw = cmdargline.get_args(pointer)[0]
        contest_id = self.parse_contest_id(contest_id_raw)
        self._data.set_data(avc_category, "contest_id", contest_id)
        text = "contest_idを{cid}に設定しました".format(cid=contest_id)
        task = create_reply_task(cmdargline.cmdline, text)
        tasks = [task]  # type: List[Union[CLBTask, List[CLBTask]]]
        return tasks

    def parse_contest_id(self, contest_id: str) -> str:
        if re.match("[0-9]+", contest_id):
            return contest_id
        url_pattern = r"https://not-522\.appspot.com/contest/([0-9]+)"
        match_url = re.match(url_pattern, contest_id)
        if match_url:
            return match_url.group(1)
        raise CLBError("contest_idの形式が不正です")


class Cmd_Img(CLBCmd):
    def __init__(self, data):
        self._keys = ["img"]
        self._documentation = "画像出力"
        self._data = data

    def run(self, cmdargline, pointer):
        contest_id = self._data.get_data(avc_category, "contest_id")
        if contest_id is None:
            raise CLBError("contest_idをsetしてください")
        text = None
        vc = AtCoderVirtualContest(contest_id, self._data)
        filename = vc.get_png_file()
        tasks = [create_reply_task(cmdargline.cmdline, text, filename)]
        return tasks


class Cmd_Download(CLBCmd):
    def __init__(self, data):
        self._keys = ["download", "dl"]
        self._documentation = "非公式APIから問題データをDL"
        self._data = data

    def run(self, cmdargline, pointer):
        api = AtCoderAPI(self._data)
        api.download()
        text = "問題データをダウンロードしました"
        tasks = [create_reply_task(cmdargline.cmdline, text)]
        return tasks


def create_avc_backend(data):
    return CmdArgBackEnd(rootcmd=RootCmd(data))
