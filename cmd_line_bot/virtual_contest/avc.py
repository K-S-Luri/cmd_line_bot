import imgkit
from typing import Union
import urllib.request
import os

from ..core.clb_data import CLBData


def download_avc(contest_id: str,
                 data: CLBData) -> None:
    url = "https://not-522.appspot.com/contest/" + contest_id
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
    html_path = os.path.join(data.get_category_dir("virtual_contest"),
                             contest_id+".html")
    png_path = os.path.join(data.get_category_dir("virtual_contest"),
                            contest_id+".png")
    with open(html_path, "w", encoding="utf-8") as f:
        print("write to %s" % html_path)
        f.write(html)
    print("write to %s" % png_path)
    imgkit.from_string(html, png_path)


def avc_test():
    data = CLBData()
    download_avc("6029001596338176", data)
