#!/usr/bin/env python3
import yaml
import os
from typing import Optional, Union, Dict

from .clb_error import CLBError


# ファイルのロックとかした方が良い？
class CLBData:
    def __init__(self,
                 config_dir: str = "~/.clb.d") -> None:
        self.config_dir = os.path.expanduser(config_dir)
        self._data = {}  # type: Dict[str, Dict[str, Union[str, int]]]
        self.load()

    def get_config_path(self) -> str:
        return os.path.join(self.config_dir, "config.yaml")

    def save(self) -> None:
        path = self.get_config_path()
        with open(path, "w", encoding="utf-8") as f:
            f.write(yaml.dump(self._data))

    def load(self) -> bool:
        path = self.get_config_path()
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as f:
            self._data = yaml.load(f)
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
