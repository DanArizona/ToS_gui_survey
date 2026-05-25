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

# from config import WindowConfig
from mb_tools.config import load_mb_config
from window_config import WindowConfig

from layout import load_widget_layout
from dialog import run_widget_selection_dialog, WidgetSelectionDialog
from window_utils import (
    is_window_visible,
    bring_window_to_front,
    update_root_window_positions,
)
from monitoring import dynamic_window_monitor
from drawing import draw_widget_bounds_filtered
from input_handlers import is_ctrl_shift_j_pressed
import pygetwindow as gw


# def run_main(logger):
def run_main(logger: logging.Logger) -> None:
    print("\n\n\n")

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

    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to project .env file. Default: .env",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed MB_* configuration loading messages.",
    )

    args = parser.parse_args()

    mb_cfg = load_mb_config(
        dotenv_path=args.env_file,
        verbose=args.verbose,
    )

    cfg = WindowConfig.from_mb_config(mb_cfg)
    cfg.print_cfg()
    cfg.log_cfg(logger)

    scans_path = mb_cfg.get_path("MB_SCANS", must_exist=False)
    logger.info("MB_SCANS = %s", scans_path)

    logger.info("WINDOW_TOS = %r", cfg.WINDOW_TOS)
    logger.info("WINDOW_TOS_MAIN = %r", cfg.WINDOW_TOS_MAIN)
    logger.info("WINDOW_TOS_LOGON = %r", cfg.WINDOW_TOS_LOGON)
    logger.info("WINDOW_TOS_UPDATE = %r", cfg.WINDOW_TOS_UPDATE)
    logger.info("WINDOW_TOS_EXPORT = %r", cfg.WINDOW_TOS_EXPORT)
    logger.info("WINDOW_TOS_WL_MAIN = %r", cfg.WINDOW_TOS_WL_MAIN)
    logger.info("WINDOW_TOS_WL_EXPORT = %r", cfg.WINDOW_TOS_WL_EXPORT)
    logger.info("WINDOW_TOS_WL_SYMBOLS = %r", cfg.WINDOW_TOS_WL_SYMBOLS)

    all_titles = [t.strip() for t in gw.getAllTitles() if t.strip()]
    logger.info("Open windows containing 'think' or 'swim':")
    for t in all_titles:
        tl = t.lower()
        if "think" in tl or "swim" in tl:
            logger.info("  %r", t)

    widget_stacks = load_widget_layout(str(cfg.WIDGET_STACK_YAML), cfg.title_map)
    update_root_window_positions(widget_stacks, cfg.title_map, logger)

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

    # logger.info(f">>> selected_widget: '{selected_widget}'")
    logger.info(">>> selected_widget: %r", selected_widget)
    print(18*"-" + "\n" + f"| selected_widget: '{selected_widget}'" + "\n" + 18*"-")

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
    update_root_window_positions(widget_stacks, cfg.title_map, logger)

    # Optional: Provide visual feedback to the user
    print("✅ Pose triggered. Window brought to front.")
    print("⏳ Waiting 5 seconds before screenshot...")

    time.sleep(5)

    bring_window_to_front(selected_widget, widget_stacks, cfg.title_map)
    update_root_window_positions(widget_stacks, cfg.title_map, logger)

    # Final window positioning before capture
    bring_window_to_front(selected_widget, widget_stacks, cfg.title_map)
    logger.info("📸 Capturing screenshot now.")
    # Draw filtered bounds
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
