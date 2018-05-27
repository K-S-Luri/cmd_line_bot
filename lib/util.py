import random, os, subprocess
import yattag
from .error import DCError
from .config import DCConfig, config

# utility関数たち
def shuffle(orig_list):
    copied_list = [orig_list[i] for i in range(len(orig_list))]
    shuffled_list = []
    while len(copied_list) > 0:
        pop_index = random.randint(0, len(copied_list)-1)
        shuffled_list.append(copied_list.pop(pop_index))
    return shuffled_list

def get_args(msg):
    return msg.content.split()[1:]

def get_cmd_line(msg):
    msg_split = msg.content.split()
    if len(msg_split) == 0:
        return None
    first_of_msg = msg_split[0]
    if first_of_msg[0] != "!":
        return None
    if (first_of_msg == "!") and (len(msg_split) >= 2):
        return msg_split[1:]
    else:
        cmd = first_of_msg[1:]
        args = msg_split[1:]
        return [cmd] + args

# Windowsでのpathの設定
def get_program_files_list():
    environ_keys = ["PROGRAMFILES", "PROGRAMFILES(X86)", "PROGRAMW6432"]
    program_files_list = []
    for key in environ_keys:
        if key not in os.environ:
            continue
        program_files = os.environ[key]
        program_files_list.append(program_files)
    return list(set(program_files_list))

def get_wkhtmltoimage_candidates():
    candidates = []
    program_files_list = get_program_files_list()
    for program_files in program_files_list:
        wkhtmltopdf_dir = os.path.join(program_files,
                                       "wkhtmltopdf",
                                       "bin")
        wkhtmltopdf_file = os.path.join(wkhtmltopdf_dir,
                                        "wkhtmltoimage.exe")
        candidates.append((wkhtmltopdf_dir, wkhtmltopdf_file))
    return candidates

def search_wkhtmltoimage():
    candidates = get_wkhtmltoimage_candidates()
    for wkhtmltopdf_dir, wkhtmltopdf_file in candidates:
        if os.path.exists(wkhtmltopdf_file):
            return wkhtmltopdf_dir
    return None

def add_wkhtmltoimage_to_path(noerror=False):
    res = subprocess.run(["where", "wkhtmltoimage"],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    returncode = res.returncode
    if returncode == 0:         # found
        return 0
    # not found
    wkhtmltopdf_dir = search_wkhtmltoimage()
    if wkhtmltopdf_dir is None:
        if noerror:
            return 1
        else:
            raise DCError("wkhtmltoimageが見つかりません")
    else:
        os.environ["Path"] += os.pathsep + wkhtmltopdf_dir

def add_xvfb_to_path():
    xvfb_dir = os.path.join(os.path.dirname(__file__),
                            "for_windows")
    os.environ["Path"] += os.pathsep + xvfb_dir
