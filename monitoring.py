# monitoring.py

from __future__ import annotations

import logging
import threading
import time
from typing import Dict

import pygetwindow as gw

from mb_tools.pseudo_widgets import WidgetStack


def is_mouse_left_down() -> bool:
    """
    Return True if the left mouse button is currently pressed.

    This helps avoid logging window movement while the user is actively
    dragging the window.
    """
    import win32api

    return win32api.GetKeyState(0x01) < 0  # 0x01 is left mouse button


def _widget_display_name(widget_stack: WidgetStack) -> str:
    """
    Return a stable display/search name for a WidgetStack.

    We intentionally derive this from path instead of using stack.name,
    because some linters may not recognize the dataclass field on the
    imported mb_tools WidgetStack.
    """
    return widget_stack.path.split("/")[-1]


def _root_widget_name(widget_stack: WidgetStack) -> str:
    """
    Return the root pseudo-widget name for this stack.
    """
    root = widget_stack.root()
    return root.path.split("/")[0]


def monitor_window_position(
    widget_stack: WidgetStack,
    logger: logging.Logger,
    poll_interval: float = 0.5,
) -> None:
    """
    Continuously track and log when a root window is moved.

    This function no longer mutates the pseudo-widget tree. It only observes
    the real OS window position and logs movement.
    """
    search_title = _root_widget_name(widget_stack)

    abs_region = widget_stack.absolute_region()
    previous_position = (abs_region.x_tl, abs_region.y_tl)

    while True:
        try:
            windows = gw.getWindowsWithTitle(search_title)

            if not windows:
                time.sleep(poll_interval)
                continue

            win = windows[0]
            new_position = (win.left, win.top)

            if new_position != previous_position and not is_mouse_left_down():
                logger.info(
                    "Window moved: %r %s -> %s",
                    search_title,
                    previous_position,
                    new_position,
                )
                previous_position = new_position

        except Exception as exc:
            logger.error("Monitor error for %r: %s", search_title, exc)

        time.sleep(poll_interval)


def dynamic_window_monitor(
    widget_stacks: Dict[str, WidgetStack],
    logger: logging.Logger,
    poll_interval: float = 2.0,
) -> None:
    """
    Supervise root widget stacks and start monitor threads for visible windows.

    Parameters
    ----------
    widget_stacks:
        Flat widget-name -> WidgetStack dictionary.

    logger:
        Logger used for status and error messages.

    poll_interval:
        Seconds between checks for visible windows.
    """
    active_threads: Dict[str, threading.Thread] = {}

    logger.info("Started dynamic window monitor")

    while True:
        try:
            current_titles = [
                title.strip()
                for title in gw.getAllTitles()
                if title.strip()
            ]

            for lookup_name, stack in widget_stacks.items():
                # Only monitor root-level stacks.
                if stack.parent is not None:
                    continue

                search_title = _root_widget_name(stack)

                is_visible = any(
                    search_title.lower() in title.lower()
                    for title in current_titles
                )

                if is_visible and lookup_name not in active_threads:
                    thread = threading.Thread(
                        target=monitor_window_position,
                        args=(stack, logger),
                        daemon=True,
                    )

                    thread.start()
                    active_threads[lookup_name] = thread

                    logger.info(
                        "Monitoring window: %s",
                        _widget_display_name(stack),
                    )

                elif not is_visible and lookup_name in active_threads:
                    logger.info("Window hidden: %s", lookup_name)
                    del active_threads[lookup_name]

        except Exception as exc:
            logger.error("Dynamic monitor error: %s", exc)

        time.sleep(poll_interval)


# # monitoring.py

# import threading
# import time
# # import logging
# import pygetwindow as gw
# from typing import Dict
# from window_utils import is_window_visible
# # from models import WidgetStack
# from mb_tools.pseudo_widgets import WidgetStack

# def is_mouse_left_down() -> bool:
#     import win32api
#     return win32api.GetKeyState(0x01) < 0  # 0x01 is left mouse button


# def monitor_window_position(widget_stack: WidgetStack, logger, poll_interval: float = 0.5):    
#     """Continuously track and log when a window is moved."""

#     # search_title = widget_stack.window_title or widget_stack.bbox.name
#     # previous_position = widget_stack.bbox.Xtl, widget_stack.bbox.Ytl
#     search_title = widget_stack.name
#     search_title = stack.name
#     previous_position = (
#         widget_stack.region.x_tl,
#         widget_stack.region.y_tl,
#     )

#     while True:
#         try:
#             windows = gw.getWindowsWithTitle(search_title)
#             if not windows:
#                 time.sleep(poll_interval)
#                 continue

#             win = windows[0]
#             new_position = (win.left, win.top)

#             if new_position != previous_position and not is_mouse_left_down():
#                 logger.info(f"Window moved: '{search_title}' {previous_position} → {new_position}")
#                 # widget_stack.bbox.Xtl, widget_stack.bbox.Ytl = new_position
#                 widget_stack.region.x_tl, widget_stack.region.y_tl = new_position
#                 previous_position = new_position

#                 widget_stack.print_tree(logger=logger)

#         except Exception as e:
#             logger.error(f"Monitor error for '{search_title}': {e}")

#         time.sleep(poll_interval)


# def dynamic_window_monitor(widget_stacks: Dict[str, WidgetStack], logger, poll_interval: float = 2.0):    
#     """
#     Supervises widget stacks and starts monitor threads for visible root windows.
#     Logs widget trees upon appearance.
#     """
#     active_threads: Dict[str, threading.Thread] = {}
#     logger.info("Started dynamic window monitor")

#     while True:
#         try:
#             logger.warning("dynamic_window_monitor")
#             current_titles = [w.strip() for w in gw.getAllTitles() if w.strip()]

#             for name, stack in widget_stacks.items():
#                 if stack.parent is not None:
#                     continue  # Only root-level stacks

#                 # search_title = stack.window_title or stack.bbox.name
#                 search_title = widget_stack.name


#                 is_visible = any(search_title.lower() in t.lower() for t in current_titles)

#                 if is_visible and name not in active_threads:
#                     thread = threading.Thread(
#                         target=monitor_window_position,
#                         args=(stack, logger),
#                         daemon=True
#                     )
#                     thread.start()
#                     active_threads[name] = thread
#                     logger.info(f"Monitoring window: {name}")

#                     # Log full widget tree when it appears
#                     stack.print_tree(logger=logger)

#                 elif not is_visible and name in active_threads:
#                     logger.info(f"Window hidden: {name}")
#                     del active_threads[name]

#         except Exception as e:
#             logger.error(f"Dynamic monitor error: {e}")

#         time.sleep(poll_interval)
