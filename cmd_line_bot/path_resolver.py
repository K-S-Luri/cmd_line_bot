import os, subprocess

# Windowsでのpathの設定
def _get_program_files_list():
    environ_keys = ["PROGRAMFILES", "PROGRAMFILES(X86)", "PROGRAMW6432"]
    program_files_list = []
    for key in environ_keys:
        if key not in os.environ:
            continue
        program_files = os.environ[key]
        program_files_list.append(program_files)
    return list(set(program_files_list))

def _get_wkhtmltoimage_candidates():
    candidates = []
    program_files_list = _get_program_files_list()
    for program_files in program_files_list:
        wkhtmltopdf_dir = os.path.join(program_files,
                                       "wkhtmltopdf",
                                       "bin")
        wkhtmltopdf_file = os.path.join(wkhtmltopdf_dir,
                                        "wkhtmltoimage.exe")
        candidates.append((wkhtmltopdf_dir, wkhtmltopdf_file))
    return candidates

def _search_wkhtmltoimage():
    candidates = _get_wkhtmltoimage_candidates()
    for wkhtmltopdf_dir, wkhtmltopdf_file in candidates:
        if os.path.exists(wkhtmltopdf_file):
            return wkhtmltopdf_dir
    return None

def _add_wkhtmltoimage_to_path(noerror=False):
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
            raise Exception("wkhtmltoimageが見つかりません")
    else:
        os.environ["Path"] += os.pathsep + wkhtmltopdf_dir

def check_wkhtmltoimage():
    if os.name == "posix":
        which_command = "which"
    elif os.name == "nt":
        _add_wkhtmltoimage_to_path(noerror=True)
        which_command = "where"
    res = subprocess.run([which_command, "wkhtmltoimage"], stdout=subprocess.PIPE)
    returncode = res.returncode
    if returncode != 0:
        if os.name == "posix":
            print("WARNING: wkhtmltoimage not found")
            print("下記のコマンドでインストールできるかもしれません．")
            print("sudo apt-get install wkhtmltopdf")
        elif os.name == "nt":
            print("WARNING: wkhtmltoimage not found")
            print("環境変数PATHおよび下記の場所を探しましたが，wkhtmltoimageが見つかりません．")
            for wkhtmltopdf_dir, wkhtmltopdf_file in _get_wkhtmltoimage_candidates():
                print(wkhtmltopdf_file)
            print("公式サイトからダウンロード・インストールして下さい．")
            print("https://wkhtmltopdf.org/downloads.html")
        return False
    path = res.stdout.decode(encoding="utf-8").rstrip()
    print("found: " + path)
    return True
