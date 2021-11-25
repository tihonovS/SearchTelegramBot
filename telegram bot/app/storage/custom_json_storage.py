import json
import pathlib

from aiogram.contrib.fsm_storage.files import _FileStorage


class CustomJSONStorage(_FileStorage):
    """
    JSON File storage based on MemoryStorage
    """

    def read(self, path: pathlib.Path):
        with path.open('r', encoding='utf8') as f:
            return json.load(f)

    def write(self, path: pathlib.Path):
        with path.open('w', encoding='utf8') as f:
            return json.dump(self.data, f, indent=4, ensure_ascii=False, default=str)
