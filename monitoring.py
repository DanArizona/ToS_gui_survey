# monitoring.py

import threading
import time
# import logging
import pygetwindow as gw
from typing import Dict
from window_utils import is_window_visible
from models import WidgetStack


def is_mouse_left_down() -> bool:
    import win32api
    return win32api.GetKeyState(0x01) < 0  # 0x01 is left mouse button


def monitor_window_position(widget_stack: WidgetStack, logger, poll_interval: float = 0.5):    
    """Continuously track and log when a window is moved."""

    search_title = widget_stack.window_title or widget_stack.bbox.name
    previous_position = widget_stack.bbox.Xtl, widget_stack.bbox.Ytl

    while True:
        try:
            windows = gw.getWindowsWithTitle(search_title)
            if not windows:
                time.sleep(poll_interval)
                continue

            win = windows[0]
            new_position = (win.left, win.top)

            if new_position != previous_position and not is_mouse_left_down():
                logger.info(f"Window moved: '{search_title}' {previous_position} → {new_position}")
                widget_stack.bbox.Xtl, widget_stack.bbox.Ytl = new_position
                previous_position = new_position

                widget_stack.print_tree(logger=logger)

        except Exception as e:
            logger.error(f"Monitor error for '{search_title}': {e}")

        time.sleep(poll_interval)


def dynamic_window_monitor(widget_stacks: Dict[str, WidgetStack], logger, poll_interval: float = 2.0):    
    """
    Supervises widget stacks and starts monitor threads for visible root windows.
    Logs widget trees upon appearance.
    """
    active_threads: Dict[str, threading.Thread] = {}
    logger.info("Started dynamic window monitor")

    while True:
        try:
            logger.warning("dynamic_window_monitor")
            current_titles = [w.strip() for w in gw.getAllTitles() if w.strip()]

            for name, stack in widget_stacks.items():
                if stack.parent is not None:
                    continue  # Only root-level stacks

                search_title = stack.window_title or stack.bbox.name
                is_visible = any(search_title.lower() in t.lower() for t in current_titles)

                if is_visible and name not in active_threads:
                    thread = threading.Thread(
                        target=monitor_window_position,
                        args=(stack, logger),
                        daemon=True
                    )
                    thread.start()
                    active_threads[name] = thread
                    logger.info(f"Monitoring window: {name}")

                    # Log full widget tree when it appears
                    stack.print_tree(logger=logger)

                elif not is_visible and name in active_threads:
                    logger.info(f"Window hidden: {name}")
                    del active_threads[name]

        except Exception as e:
            logger.error(f"Dynamic monitor error: {e}")

        time.sleep(poll_interval)
