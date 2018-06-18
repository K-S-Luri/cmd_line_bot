#!/usr/bin/env python3
import json
import os
from typing import Optional, Union, Dict
from clb_error import CLBError


# ファイルのロックとかした方が良い？
class CLBData:
    def __init__(self, path: str) -> None:
        self.path = os.path.expanduser(path)
        self._data = {}  # type: Dict[str, Dict[str, Union[str, int]]]
        self.load()

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=4)

    def load(self) -> bool:
        if not os.path.exists(self.path):
            return False
        with open(self.path, "r", encoding="utf-8") as f:
            self._data = json.load(f)
            return True

    def get(self, category: str, key: str) -> Optional[Union[str, int]]:
        data = self._data
        if category not in data:
            raise CLBError("カテゴリ'%s'が見つかりません" % category)
        if key in data[category]:
            return data[category][key]
        else:
            return None

    def set(self, category: str, key: str,
            value: Union[str, int]) -> None:
        self._data[category][key] = value

    def add_category(self, category: str) -> None:
        if category not in self._data.keys():
            self._data[category] = {}
