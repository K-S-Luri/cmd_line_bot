#! python3
# -*- coding: utf-8 -*-

from platform import python_version
from distutils.version import StrictVersion
import os, subprocess, pip


def check_python_version():
    if StrictVersion(python_version()) >= StrictVersion("3.5"):
        print("version: %s OK" % python_version())
        return True
    else:
        print("version: %s NG" % python_version())
        print("pythonのバージョンは3.5以上が必要です")
        print("アップデートして下さい")
        return False

# インストールされているパッケージ一覧
def check_packages():
    installed_package_list = list(map(lambda dist: dist.project_name,
                                      pip.utils.get_installed_distributions(local_only=True)))
    install_failed = []
    # discordをインストール
    if "discord.py" not in installed_package_list:
        install_status = pip.main(["install", "-U", "discord.py"])
        if install_status != 0:
            install_failed.append("discord")
    # その他のパッケージたち
    packages = ["imgkit", "yattag"]
    for pkg in packages:
        if pkg in installed_package_list:
            print("found: %s" % pkg)
        else:
            install_status = pip.main(["install", pkg])
            if install_status == 0:
                print("installed: %s" % pkg)
            else:
                install_failed.append(pkg)
    if len(install_failed) > 0:
        print("インストールに失敗しました: %s" % install_failed)
        return False
    else:
        return True

def check_wkhtmltoimage():
    if os.name == "posix":
        which_command = "which"
        # res = subprocess.run(["which", "wkhtmltoimage"], stdout=subprocess.PIPE)
        # returncode = res.returncode
        # if returncode != 0:
        #     print("wkhtmltoimageが見つかりません")
        #     print("公式サイトからダウンロード・インストールして下さい")
        #     return False
    elif os.name == "nt":
        from sjlib.sjutil import add_wkhtmltoimage_to_path
        # from sjlib.sjerror import SJError
        add_wkhtmltoimage_to_path(noerror=True)
        # try:
        #     add_wkhtmltoimage_to_path()
        # except SJError:
        #     print("wkhtmltoimageが見つかりません")
        #     print("公式サイトからダウンロード・インストールして下さい")
        #     return False
        which_command = "where"
    res = subprocess.run([which_command, "wkhtmltoimage"], stdout=subprocess.PIPE)
    returncode = res.returncode
    if returncode != 0:
        if os.name == "posix":
            print("wkhtmltoimageが見つかりません．")
            print("下記のコマンドでインストールできるかもしれません．")
            print("sudo apt-get install wkhtmltopdf")
        elif os.name == "nt":
            from sjlib.sjutil import get_wkhtmltoimage_candidates
            print("環境変数PATHおよび下記の場所を探しましたが，wkhtmltoimageが見つかりません．")
            for wkhtmltopdf_dir, wkhtmltopdf_file in get_wkhtmltoimage_candidates():
                print(wkhtmltopdf_file)
            print("公式サイトからダウンロード・インストールして下さい．")
            print("https://wkhtmltopdf.org/downloads.html")
        return False
    path = res.stdout.decode(encoding="utf-8").rstrip()
    print("found: " + path)
    return True


setup_success = check_python_version() and check_packages() and check_wkhtmltoimage()

print("------------")

if setup_success:
    print("setupに成功しました")
else:
    print("setupに失敗しました．上記のメッセージを参考にして修正して下さい．")

# ダブルクリックで起動した際に，終了後に閉じない
print("Enterキーを押すと閉じます")
if StrictVersion(python_version()) >= StrictVersion("3.0"):
    input()
else:
    raw_input()
