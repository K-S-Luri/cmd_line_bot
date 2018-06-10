#!/usr/bin/env python3
import json, os
from clb_error import CLBError

# ファイルのロックとかした方が良い？
class CLBData:
    def __init__(self, path):
        self.path = os.path.expanduser(path)
        self._data = {}
        self.load()
    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=4)
    def load(self):
        if not os.path.exists(self.path):
            return False
        with open(self.path, "r", encoding="utf-8") as f:
            self._data = json.load(f)
            return True
    def get(self, category, key):
        data = self._data
        if category not in data:
            raise CLBError("カテゴリ'%s'が見つかりません" % category)
        if key in data[category]:
            return data[category][key]
        else:
            return None
    def set(self, category, key, value):
        self._data[category][key] = value
    def add_category(self, category):
        if category not in self._data.keys():
            self._data[category] = {}
