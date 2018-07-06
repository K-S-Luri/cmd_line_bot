from typing import List, Union, cast, Callable
import re

from .avc import AtCoderVirtualContest, AtCoderAPI
from ..core.clb_interface import CLBTask, CLBTask_Msg, CLBTask_DM, CLBTask_Gathered, create_reply_task
from ..core.clb_error import CLBError
from ..core.clb_data import CLBData
from ..ends.cmd_arg_backend import CmdArgBackEnd, CLBCmd, CLBCmdWithSub, CLBCmdArgLine


class AVCData:
    def __init__(self, clb_data):
        self.clb_data = clb_data
        self.category = "virtual_contest"
        self.old_AC_dict = None


class RootCmd(CLBCmdWithSub):
    def __init__(self, avc_data: AVCData) -> None:
        self._documentation = "root command"
        self._subcmds = [Cmd_Show(avc_data),
                         Cmd_Set(avc_data),
                         Cmd_Img(avc_data),
                         Cmd_Download(avc_data),
                         Cmd_AC(avc_data)]


class Cmd_Show(CLBCmd):
    def __init__(self, avc_data: AVCData) -> None:
        self._keys = ["show"]
        self._documentation = "バチャコンの概要を表示"
        self._avc_data = avc_data
        self._data = self._avc_data.clb_data

    def run(self, cmdargline, pointer, send_task):
        avc_category = self._avc_data.category
        contest_id = self._data.get_data(avc_category, "contest_id")
        if contest_id is None:
            raise CLBError("contest_idをsetしてください")
        vc = AtCoderVirtualContest(contest_id, self._data)
        vc_info = vc.get_contest_info()
        # print(vc_info)
        task = create_reply_task(cmdargline.cmdline, vc_info)
        send_task(task)


class Cmd_Set(CLBCmd):
    def __init__(self, avc_data: AVCData) -> None:
        self._keys = ["set"]
        self._documentation = "バチャコンの contest_id を設定する．URLコピペでも，数字のみでもOK"
        self._avc_data = avc_data
        self._data = self._avc_data.clb_data

    def run(self,
            cmdargline: CLBCmdArgLine,
            pointer: int,
            send_task: Callable[[CLBTask], None]) -> None:
        if cmdargline.get_num_args(pointer) < 1:
            raise CLBError("引数が足りません")
        elif cmdargline.get_num_args(pointer) > 1:
            raise CLBError("引数が多すぎます")
        contest_id_raw = cmdargline.get_args(pointer)[0]
        contest_id = self.parse_contest_id(contest_id_raw)
        avc_category = self._avc_data.category
        self._data.set_data(avc_category, "contest_id", contest_id)
        self._avc_data.old_AC_dict = None  # 問題が変わったので，AC 情報もリセット
        text = "contest_idを{cid}に設定しました".format(cid=contest_id)
        task = create_reply_task(cmdargline.cmdline, text)
        send_task(task)
        # tasks = [task]  # type: List[Union[CLBTask, List[CLBTask]]]
        # return tasks

    def parse_contest_id(self, contest_id: str) -> str:
        if re.match("[0-9]+", contest_id):
            return contest_id
        url_pattern = r"https://not-522\.appspot.com/contest/([0-9]+)"
        match_url = re.match(url_pattern, contest_id)
        if match_url:
            return match_url.group(1)
        raise CLBError("contest_idの形式が不正です")


class Cmd_Img(CLBCmd):
    def __init__(self, avc_data: AVCData) -> None:
        self._keys = ["img"]
        self._documentation = "バチャコンのhtmlを画像にして送信"
        self._avc_data = avc_data
        self._data = self._avc_data.clb_data

    def run(self, cmdargline, pointer, send_task):
        avc_category = self._avc_data.category
        contest_id = self._data.get_data(avc_category, "contest_id")
        if contest_id is None:
            raise CLBError("contest_idをsetしてください")
        text = None
        vc = AtCoderVirtualContest(contest_id, self._data)
        filename = vc.get_png_file()
        task = create_reply_task(cmdargline.cmdline, text, filename)
        send_task(task)


class Cmd_Download(CLBCmd):
    def __init__(self, avc_data: AVCData) -> None:
        self._keys = ["download", "dl"]
        self._documentation = "非公式APIから問題データをDL，バチャコンのhtmlをDl"
        self._avc_data = avc_data
        self._data = self._avc_data.clb_data

    def run(self, cmdargline, pointer, send_task):
        api = AtCoderAPI(self._data)
        api.download()
        text = "AtCoder非公式APIから問題データをダウンロードしました"
        task = create_reply_task(cmdargline.cmdline, text)
        send_task(task)
        avc_category = self._avc_data.category
        contest_id = self._data.get_data(avc_category, "contest_id")
        if contest_id is not None:
            vc = AtCoderVirtualContest(contest_id, self._data)
            vc.download()
            text = "バチャコンのhtmlをダウンロードしました"
            task = create_reply_task(cmdargline.cmdline, text)
            send_task(task)


class Cmd_AC(CLBCmdWithSub):
    def __init__(self, avc_data: AVCData) -> None:
        self._keys = ["ac", "AC"]
        self._documentation = "AC 通知を扱う．サブコマンドを取る．"
        self._subcmds = [Cmd_AC_Show(avc_data),
                         Cmd_AC_Enable(avc_data),
                         Cmd_AC_Disable(avc_data)]


class Cmd_AC_Enable(CLBCmd):
    def __init__(self, avc_data: AVCData) -> None:
        self._keys = ["enable", "e"]
        self._documentation = "自動 AC 通知を有効化する"
        self._avc_data = avc_data
        self._data = self._avc_data.clb_data

    def run(self, cmdargline, pointer, send_task):
        category = self._avc_data.category
        self._data.set_memory(category, "enable_AC_check", True)
        text = "自動 AC 通知を有効化しました"
        task = create_reply_task(cmdargline.cmdline, text)
        send_task(task)


class Cmd_AC_Disable(CLBCmd):
    def __init__(self, avc_data: AVCData) -> None:
        self._keys = ["disable", "d"]
        self._documentation = "自動 AC 通知を無効化する"
        self._avc_data = avc_data
        self._data = self._avc_data.clb_data

    def run(self, cmdargline, pointer, send_task):
        category = self._avc_data.category
        self._data.set_memory(category, "enable_AC_check", False)
        text = "自動 AC 通知を無効化しました"
        task = create_reply_task(cmdargline.cmdline, text)
        send_task(task)


class Cmd_AC_Show(CLBCmd):
    def __init__(self, avc_data: AVCData) -> None:
        self._keys = ["show"]
        self._documentation = "新たなACの一覧を表示"
        self._avc_data = avc_data
        self._data = self._avc_data.clb_data

    def run(self, cmdargline, pointer, send_task):
        category = self._avc_data.category
        enable_AC_check = self._data.get_memory(category, "enable_AC_check")
        if cmdargline.get_num_args(pointer) > 1:
            raise CLBError("引数が多すぎます")
        elif cmdargline.get_num_args(pointer) == 0:
            verbose = True
        else:
            arg = cmdargline.get_args(pointer)[0]
            if arg == "fromcron":
                if not enable_AC_check:  # None or False
                    return
                verbose = False
            else:
                raise CLBError("不正な引数: {arg}".format(arg=arg))
        avc_category = self._avc_data.category
        contest_id = self._data.get_data(avc_category, "contest_id")
        old_AC_dict = self._avc_data.old_AC_dict
        new_vc = AtCoderVirtualContest(contest_id, self._data)
        if verbose:
            text = "バチャコンのhtmlをDLしています…"
            task = create_reply_task(cmdargline.cmdline, text)
            send_task(task)
        new_vc.download()
        self._avc_data.old_AC_dict = new_vc.get_AC_dict()
        new_AC_list = new_vc.get_new_AC_list(old_AC_dict)
        for new_AC in new_AC_list:
            username, problem_number, problem_score = new_AC
            problem = new_vc.get_problem(problem_number)
            problem_str = "{title} ({score})".format(title=problem.get_title(),
                                                     score=problem_score)
            text = "[AC]{username}: {problem_info}".format(username=username, problem_info=problem_str)
            task = create_reply_task(cmdargline.cmdline, text)
            send_task(task)
        if verbose and (len(new_AC_list) == 0):
            text = "誰も新たなACはしてないよ"
            task = create_reply_task(cmdargline.cmdline, text)
            send_task(task)


def create_avc_backend(data: CLBData) -> CmdArgBackEnd:
    avc_data = AVCData(data)
    return CmdArgBackEnd(rootcmd=RootCmd(avc_data))
