# window_utils.py 
from __future__ import annotations
from dataclasses import replace
import logging
import time
import win32process
import psutil

import pygetwindow as gw
from typing import Optional
import pandas as pd
# from models import WidgetStack
from mb_tools.pseudo_widgets import WidgetStack

import win32gui
import win32con
import win32api


def find_window_by_title_prefix(title_prefix: str):
    """
    Find an OS window whose title starts with title_prefix.

    This is intended for application windows whose right side changes,
    such as:
        Main@thinkorswim [build 1991]
        Main@thinkorswim [build 1992]

    The title_map should therefore contain stable leftmost title prefixes.
    """
    prefix = title_prefix.strip().lower()

    if not prefix:
        return None

    all_windows = [
        w for w in gw.getAllWindows()
        if w.title and w.title.strip() and w.width > 0 and w.height > 0
    ]

    matches = [
        w for w in all_windows
        if w.title.strip().lower().startswith(prefix)
    ]

    if not matches:
        return None

    # Prefer visible windows if pygetwindow supports isVisible on this platform.
    visible_matches = [
        w for w in matches
        if getattr(w, "isVisible", True)
    ]

    if visible_matches:
        return visible_matches[0]

    return matches[0]



def get_process_name(hwnd) -> Optional[str]:
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return psutil.Process(pid).name()
    except Exception:
        return None

def get_windows_dataframe() -> pd.DataFrame:
    windows = gw.getAllWindows()
    window_data = []

    for w in windows:
        if w.title:
            hwnd = w._hWnd
            process_name = get_process_name(hwnd)
            is_uwp = process_name and process_name.lower() == "applicationframehost.exe"

            window_data.append({
                'Title': w.title,
                'Left': w.left,
                'Top': w.top,
                'Width': w.width,
                'Height': w.height,
                'IsActive': w.isActive,
                'IsMaximized': w.isMaximized,
                'IsMinimized': w.isMinimized,
                'ProcessName': process_name,
                'IsUWP': is_uwp
            })

    df = pd.DataFrame(window_data)
    return df.sort_values(by='Title').reset_index(drop=True)





# def bring_window_to_front(widget_name: str, widget_stacks: dict[str, WidgetStack], title_map: dict[str, str]):
#     if widget_name not in widget_stacks:
#         return

#     stack = widget_stacks[widget_name]
#     while stack.parent:
#         stack = stack.parent

#     search_title = title_map.get(stack.root().name, stack.root().name)
#     windows = gw.getWindowsWithTitle(search_title)
#     if windows:
#         win = windows[0]
#         if win.isMinimized:
#             win.restore()
#         try:
#             win.activate()
#         except Exception as e:
#             logging.error(f"Failed to activate window '{search_title}': {e}")
# def bring_window_to_front(
#     widget_name: str,
#     widget_stacks: dict[str, WidgetStack],
#     title_map: dict[str, str],
# ) -> None:
#     if widget_name not in widget_stacks:
#         return

#     root = widget_stacks[widget_name].root()
#     search_title = title_map.get(root.name, root.name)

#     windows = gw.getWindowsWithTitle(search_title)

#     if windows:
#         win = windows[0]

#         if win.isMinimized:
#             win.restore()

#         try:
#             win.activate()
#         except Exception as e:
#             logging.error(f"Failed to activate window '{search_title}': {e}")





# def is_window_visible(widget_name: str, widget_stacks: dict[str, WidgetStack], title_map: dict[str, str]) -> bool:
#     if widget_name not in widget_stacks:
#         return False

#     stack = widget_stacks[widget_name]
#     while stack.parent:
#         stack = stack.parent

#     # search_title = title_map.get(stack.bbox.name, stack.bbox.name)
#     search_title = title_map.get(stack.root().name, stack.root().name)
#     titles = [title.strip().lower() for title in gw.getAllTitles() if title.strip()]
#     return any(search_title.lower() in t for t in titles)




# def is_window_visible(
#     widget_name: str,
#     widget_stacks: dict[str, WidgetStack],
#     title_map: dict[str, str],
# ) -> bool:
#     if widget_name not in widget_stacks:
#         return False

#     root = widget_stacks[widget_name].root()
#     search_title = title_map.get(root.name, root.name)

#     titles = [
#         title.strip().lower()
#         for title in gw.getAllTitles()
#         if title.strip()
#     ]

#     return any(search_title.lower() in title for title in titles)



def is_window_visible(widget_name, widget_stacks, title_map) -> bool:
    root_name = widget_stacks[widget_name].root().name
    title_prefix = title_map[root_name]
    window = find_window_by_title_prefix(title_prefix)
    return window is not None








# def update_root_window_positions(widget_stacks, title_map, logger=None) -> None:
#     """
#     Update top-level pseudo-widget X/Y positions from current OS window positions.

#     title_map values are stable window-title prefixes.
#     YAML width/height are left unchanged.
#     Only root widget X/Y values are updated.
#     """
#     for root_name, title_prefix in title_map.items():
#         root_widget = widget_stacks.get(root_name)

#         if root_widget is None:
#             if logger:
#                 logger.warning(
#                     "Root widget %r from title_map was not found in widget_stacks.",
#                     root_name,
#                 )
#             continue

#         window = find_window_by_title_prefix(title_prefix)

#         if window is None:
#             if logger:
#                 logger.warning(
#                     "Could not find OS window for root widget %r using title prefix %r.",
#                     root_name,
#                     title_prefix,
#                 )
#             continue

#         old_x = root_widget.region.x_tl
#         old_y = root_widget.region.y_tl

#         root_widget.region.x_tl = window.left
#         root_widget.region.y_tl = window.top

#         if logger:
#             logger.info(
#                 "Updated root %s from OS window title prefix %r: "
#                 "matched title=%r, old=(%s, %s), new=(%s, %s), "
#                 "yaml_size=(%s, %s), os_size=(%s, %s)",
#                 root_name,
#                 title_prefix,
#                 window.title,
#                 old_x,
#                 old_y,
#                 root_widget.region.x_tl,
#                 root_widget.region.y_tl,
#                 root_widget.region.width,
#                 root_widget.region.height,
#                 window.width,
#                 window.height,
#             )



def update_root_window_positions(
    widget_stacks,
    title_map,
    logger=None,
    *,
    size_tolerance: int = 4,
) -> None:
    """
    Update top-level pseudo-widget X/Y positions from current OS window positions.

    The title_map values are stable window-title prefixes.

    YAML width/height are left unchanged.
    Only the root widget X/Y values are updated.

    If the OS window size differs significantly from the YAML size,
    log a warning.
    """
    for root_name, title_prefix in title_map.items():
        root_widget = widget_stacks.get(root_name)

        if root_widget is None:
            if logger:
                logger.warning(
                    "Root widget %r from title_map was not found in widget_stacks.",
                    root_name,
                )
            continue

        window = find_window_by_title_prefix(title_prefix)

        if window is None:
            if logger:
                logger.warning(
                    "Could not find OS window for root widget %r using title prefix %r.",
                    root_name,
                    title_prefix,
                )
            continue

        # Compare YAML size to actual OS window size.
        yaml_width = root_widget.region.width
        yaml_height = root_widget.region.height
        os_width = window.width
        os_height = window.height

        width_diff = os_width - yaml_width
        height_diff = os_height - yaml_height

        if abs(width_diff) > size_tolerance or abs(height_diff) > size_tolerance:
            if logger:
                logger.warning(
                    "Window size differs from YAML for root %r matched by prefix %r. "
                    "YAML size=(%s, %s), OS size=(%s, %s), diff=(%+d, %+d). "
                    "Child widget positions may be inaccurate.",
                    root_name,
                    title_prefix,
                    yaml_width,
                    yaml_height,
                    os_width,
                    os_height,
                    width_diff,
                    height_diff,
                )

        # # Update only the runtime top-left position.
        # old_x = root_widget.region.x_tl
        # old_y = root_widget.region.y_tl

        # root_widget.region.x_tl = window.left
        # root_widget.region.y_tl = window.top

        # if logger:
        #     logger.info(
        #         "Updated root %s from OS window title prefix %r: "
        #         "matched title=%r, old=(%s, %s), new=(%s, %s), "
        #         "yaml_size=(%s, %s), os_size=(%s, %s)",
        #         root_name,
        #         title_prefix,
        #         window.title,
        #         old_x,
        #         old_y,
        #         root_widget.region.x_tl,
        #         root_widget.region.y_tl,
        #         yaml_width,
        #         yaml_height,
        #         os_width,
        #         os_height,
        #     )


        old_x = root_widget.region.x_tl
        old_y = root_widget.region.y_tl

        root_widget.region = replace(
            root_widget.region,
            x_tl=window.left,
            y_tl=window.top,
        )

        if logger:
            logger.info(
                "Updated root %s from OS window title prefix %r: "
                "matched title=%r, old=(%s, %s), new=(%s, %s), "
                "yaml_size=(%s, %s), os_size=(%s, %s)",
                root_name,
                title_prefix,
                window.title,
                old_x,
                old_y,
                root_widget.region.x_tl,
                root_widget.region.y_tl,
                yaml_width,
                yaml_height,
                os_width,
                os_height,
            )




# def bring_window_to_top(window_title: str) -> bool:
#     """Bring a window to the front given its title. Return True on success."""
#     windows = gw.getWindowsWithTitle(window_title)
#     if not windows:
#         return False

#     try:
#         win = windows[0]
#         win.activate()
#         return True
#     except Exception as e:
#         logging.error(f"Failed to bring window '{window_title}' to top: {e}")
#         return False


# def bring_window_to_front(widget_name, widget_stacks, title_map) -> bool:
#     root_name = widget_stacks[widget_name].root().name
#     title_prefix = title_map[root_name]
#     window = find_window_by_title_prefix(title_prefix)

#     if window is None:
#         return False

#     window.activate()
#     return True


def bring_window_to_front(widget_name, widget_stacks, title_map, logger=None) -> bool:
    root_name = widget_stacks[widget_name].root().name
    title_prefix = title_map[root_name]

    window = find_window_by_title_prefix(title_prefix)

    if window is None:
        if logger:
            logger.warning(
                "Could not bring window to front. No match for root %r using prefix %r.",
                root_name,
                title_prefix,
            )
        return False

    try:
        if window.isMinimized:
            window.restore()

        window.activate()

        if logger:
            logger.info(
                "Brought window to front: root=%r prefix=%r matched=%r",
                root_name,
                title_prefix,
                window.title,
            )

        return True

    except Exception as exc:
        if logger:
            logger.exception(
                "Failed to bring window to front: root=%r prefix=%r matched=%r",
                root_name,
                title_prefix,
                window.title,
            )
        return False