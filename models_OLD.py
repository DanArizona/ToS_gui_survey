# models.py

from dataclasses import dataclass
from typing import Optional, Union
import numpy as np
import pandas as pd
import pyautogui
import pytesseract
from PIL import Image
# import logging


@dataclass
class WidgetBBox:
    name: str
    width: int
    height: int
    Xtl: int
    Ytl: int

    @classmethod
    def from_dataframe_row(cls, row: Union[dict, 'pd.Series']):
        return cls(
            name=row['Title'],
            width=int(row['Width']),
            height=int(row['Height']),
            Xtl=int(row['Left']),
            Ytl=int(row['Top'])
        )

    def center(self) -> tuple[int, int]:
        return (
            self.Xtl + self.width // 2,
            self.Ytl + self.height // 2
        )

    def compare_to(self, other: 'WidgetBBox') -> dict:
        return {
            'width_diff': self.width - other.width,
            'height_diff': self.height - other.height,
            'Xtl_diff': self.Xtl - other.Xtl,
            'Ytl_diff': self.Ytl - other.Ytl
        }

    def capture_and_analyze(self) -> dict:
        bbox = (self.Xtl, self.Ytl, self.Xtl + self.width, self.Ytl + self.height)
        screenshot = pyautogui.screenshot(region=bbox)

        text = pytesseract.image_to_string(screenshot)
        gray = screenshot.convert('L')
        pixels = np.array(gray)
        stddev = float(np.std(pixels))

        return {
            'ocr_text': text.strip(),
            'grayscale_stddev': stddev,
            'width': self.width,
            'height': self.height
        }


class WidgetStack:
    def __init__(self, bbox: WidgetBBox, parent: Optional['WidgetStack'] = None, window_title: Optional[str] = None):
        self.bbox = bbox
        self.parent = parent
        self.children: list[WidgetStack] = []
        self.window_title = window_title
        if parent:
            parent.children.append(self)

    def is_root(self) -> bool:
        return self.parent is None

    def ancestry(self) -> list[str]:
        lineage = []
        current = self
        while current:
            lineage.append(current.bbox.name)
            current = current.parent
        return lineage[::-1]

    def get_absolute_position(self) -> tuple[int, int]:
        x, y = self.bbox.Xtl, self.bbox.Ytl
        current = self.parent
        while current:
            x += current.bbox.Xtl
            y += current.bbox.Ytl
            current = current.parent
        return x, y

    def get_absolute_center(self) -> tuple[int, int]:
        x, y = self.get_absolute_position()
        return x + self.bbox.width // 2, y + self.bbox.height // 2


    def print_tree(self, 
                   prefix: str = "", 
                   is_last: bool = True, 
                   log: bool = True, 
                   logger=None):
        """
        Print or log the widget tree. If `logger` is provided and `log=True`, use logger; otherwise print.
        """
        from pygetwindow import getAllTitles

        connector = "└── " if is_last else "├── "
        abs_x, abs_y = self.get_absolute_position()
        position_str = f"<{abs_x}, {abs_y}>"

        visibility_note = ""
        if self.parent is None:
            all_titles = [title.strip().lower() for title in getAllTitles() if title.strip()]
            search_title = self.window_title or self.bbox.name
            is_visible = any(search_title.lower() in title for title in all_titles)
            visibility_note = " [VISIBLE]" if is_visible else " [HIDDEN]"

        line = (
            f"{prefix}{connector}{self.bbox.name} "
            f"[{self.bbox.Xtl}, {self.bbox.Ytl}] {self.bbox.width}x{self.bbox.height} "
            f"{position_str}{visibility_note}"
        )

        if log and logger:
            logger.info(line)
        elif log:
            print(line)
        else:
            print(line)

        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(self.children):
            child.print_tree(prefix=new_prefix, is_last=(i == len(self.children) - 1), log=log, logger=logger)

    def find_widget(self, name: str) -> Optional['WidgetStack']:
        if self.bbox.name == name:
            return self
        for child in self.children:
            found = child.find_widget(name)
            if found:
                return found
        return None

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        return self is other
