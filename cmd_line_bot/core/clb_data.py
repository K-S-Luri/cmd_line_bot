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
        self._config = {}  # type: Dict[str, Dict[str, Union[str, int]]]
        self.load_config()

    def get_config_path(self) -> str:
        return os.path.join(self.config_dir, "config.yaml")

    def get_category_dir(self, category: str) -> str:
        path = os.path.join(self.config_dir, category)
        os.makedirs(path, exist_ok=True)
        return path

    # def save(self) -> None:
    #     path = self.get_config_path()
    #     with open(path, "w", encoding="utf-8") as f:
    #         f.write(yaml.dump(self._data))

    def load_config(self) -> bool:
        path = self.get_config_path()
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as f:
            self._config = yaml.load(f)
            return True

    def get_config(self, category: str, key: str) -> Optional[Union[str, int]]:
        data = self._config
        if data is None:
            raise CLBError("設定ファイル%sが空です" % self.get_config_path())
        if category not in data:
            raise CLBError("カテゴリ'%s'が見つかりません" % category)
        if key in data[category]:
            return data[category][key]
        else:
            return None

    def get_data(self,
                 category: str,
                 key: str) -> Optional[Union[str, int]]:
        path = os.path.join(self.get_category_dir(category), "data.yaml")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.load(f)
            if data is None:
                data = {}
        if key in data.keys():
            res = data[key]
        else:
            res = None
        return res

    def set_data(self,
                 category: str,
                 key: str,
                 value: Union[str, int]) -> None:
        path = os.path.join(self.get_category_dir(category), "data.yaml")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.load(f)
            if data is None:
                data = {}
        else:
            data = {}
        data[key] = value
        with open(path, "w", encoding="utf-8") as f:
            f.write(yaml.dump(data))

    # def add_category(self, category: str) -> None:
    #     if category not in self._data.keys():
    #         self._data[category] = {}
