"""
Main entry point for widget surveying and visualization tool.

Usage:

    python widget_check.py
        If no widget names are supplied, a PySide6 dialog will prompt the user to select one.

    python widget_check.py widget_name
        Specifies the widgets of interest

        Once the script has the name of the widget, execution waits for the user.
        Key combination  <shft>+<ctrl>+J  triggers a 5 second timer, allowing the user to ready the UI.
        At 5 seconds, the trigger will 
            - take a full screen snapshot
            - draw bounding boxes of the specidfied widget as well as the widgets in its stack/tree
            - popup a display of the resulting graphic

    python widget_check.py -h    displays this help on the terminal
    python widget_check.py --h      "      "    "   "   "     "
    
"""

import sys
import time
import argparse
import threading
import logging
from typing import Optional

from config import WindowConfig
from layout import load_widget_layout
from dialog import run_widget_selection_dialog, WidgetSelectionDialog
from window_utils import (
    is_window_visible,
    bring_window_to_front
)
from monitoring import dynamic_window_monitor
from drawing import draw_widget_bounds_filtered
from input_handlers import is_ctrl_shift_j_pressed
import pygetwindow as gw

def run_main(logger):
    parser = argparse.ArgumentParser(
        description="Draw widget bounds for specified widget names."
    )

    parser.add_argument(
        "widgets",
        nargs="*",
        help="List of widget names to draw (e.g. btn_action_menu pick_to_file)",
    )

    parser.add_argument(
        "--no-raw-capture",
        action="store_true",
        help="Do not save the raw screenshot without drawn shapes.",
    )

    args = parser.parse_args()

    cfg = WindowConfig()
    cfg.print_cfg()

    logger.info(f"WINDOW_TOS = {cfg.WINDOW_TOS!r}")
    logger.info(f"WINDOW_TOS_MAIN = {cfg.WINDOW_TOS_MAIN!r}")
    logger.info(f"WINDOW_TOS_LOGON = {cfg.WINDOW_TOS_LOGON!r}")
    logger.info(f"WINDOW_TOS_UPDATE = {cfg.WINDOW_TOS_UPDATE!r}")
    logger.info(f"WINDOW_TOS_EXPORT = {cfg.WINDOW_TOS_EXPORT!r}")
    logger.info(f"WINDOW_TOS_WL_MAIN = {cfg.WINDOW_TOS_WL_MAIN!r}")
    logger.info(f"WINDOW_TOS_WL_EXPORT = {cfg.WINDOW_TOS_WL_EXPORT!r}")
    logger.info(f"WINDOW_TOS_WL_SYMBOLS = {cfg.WINDOW_TOS_WL_SYMBOLS!r}")

    all_titles = [t.strip() for t in gw.getAllTitles() if t.strip()]
    logger.info("Open windows containing 'think' or 'swim':")
    for t in all_titles:
        tl = t.lower()
        if "think" in tl or "swim" in tl:
            logger.info(f"  {t!r}")



    # print("\nMKTBOT_SCANS =", cfg.MKTBOT_SCANS, "\n")
    logger.info(f"MKTBOT_SCANS = {cfg.MKTBOT_SCANS}")

    widget_stacks = load_widget_layout(cfg.WIDGET_STACK_YAML, cfg.title_map)

    # Determine which widget(s) to work with
    if not args.widgets:
        selected_widget = run_widget_selection_dialog(list(widget_stacks.keys()))
        if not selected_widget:
            print("No widget selected. Exiting.")
            # sys.exit(0)
            return
    else:
        selected_widget = args.widgets[0]
        if selected_widget not in widget_stacks:
            print(f"Invalid widget name: {selected_widget}")
            # sys.exit(1)
            return

    # Attempt to bring window to front
    if is_window_visible(selected_widget, widget_stacks, cfg.title_map):
        bring_window_to_front(selected_widget, widget_stacks, cfg.title_map)
    else:
        print(f"⚠️  Warning: Window for widget '{selected_widget}' is not visible. Monitoring will continue.")

    # Start dynamic monitor in a background thread
    supervisor = threading.Thread(
        target=dynamic_window_monitor,
        args=(widget_stacks, logger),
        daemon=True
    )
    supervisor.start()

    # Wait for pose trigger
    # print("\nWaiting for pose trigger (Ctrl+Shift+J)...")
    logger.info("Waiting for pose trigger (Ctrl+Shift+J)...")
    print("\nWaiting for pose trigger (Ctrl+Shift+J)...")
    while not is_ctrl_shift_j_pressed():
        time.sleep(0.1)

    # Verify visibility again before capture
    if not is_window_visible(selected_widget, widget_stacks, cfg.title_map):
        # print(f"❌ Cannot trigger pose: Window for widget '{selected_widget}' is still not visible.")
        logger.error(f"❌ Cannot trigger pose: Window for widget '{selected_widget}' is still not visible.")
        sys.exit(1)

    logger.info("✅ Pose triggered. Bringing window to front and waiting 5 seconds...")
    bring_window_to_front(selected_widget, widget_stacks, cfg.title_map)

    # Optional: Provide visual feedback to the user
    print("✅ Pose triggered. Window brought to front.")
    print("⏳ Waiting 5 seconds before screenshot...")

    time.sleep(5)

    # Final window positioning before capture
    bring_window_to_front(selected_widget, widget_stacks, cfg.title_map)
    logger.info("📸 Capturing screenshot now.")
    # Draw filtered bounds
    # draw_widget_bounds_filtered(widget_stacks, [selected_widget], logger)

    # capture_paths = draw_widget_bounds_filtered(
    #     widget_stacks,
    #     [selected_widget],
    #     logger,
    #     capture_dir="captures",
    #     yaml_path=cfg.WIDGET_STACK_YAML,
    #     save_raw=True,
    #     show_image=True,
    # )

    capture_paths = draw_widget_bounds_filtered(
        widget_stacks,
        [selected_widget],
        logger,
        capture_dir="captures",
        yaml_path=cfg.WIDGET_STACK_YAML,
        save_raw=not args.no_raw_capture,
        show_image=True,
    )

    logger.info("Capture files:")
    for label, path in capture_paths.items():
        logger.info("  %s: %s", label, path)


if __name__ == "__main__":

    from logger import setup_logger
    logger = setup_logger()

    run_main(logger)
