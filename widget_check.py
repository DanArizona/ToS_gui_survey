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
# from typing import Optional

# from config import WindowConfig
# from mb_tools.config import load_mb_config
from mb_tools.config import MBConfig, load_mb_config
from window_config import WindowConfig

from layout import load_widget_layout
# from dialog import run_widget_selection_dialog, WidgetSelectionDialog
from dialog import run_widget_selection_dialog
from window_utils import (
    is_window_visible,
    bring_window_to_front,
    update_root_window_positions,
)
from monitoring import dynamic_window_monitor
from drawing import draw_widget_bounds_filtered
from input_handlers import is_ctrl_shift_j_pressed
import pygetwindow as gw



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Draw widget bounds for specified widget names."
    )

    parser.add_argument(
        "widgets",
        nargs="*",
        help="List of widget names to draw, e.g. btn_action_menu pick_to_file.",
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

    return parser



def load_runtime_config(
    args: argparse.Namespace,
    logger: logging.Logger,
) -> tuple[object, WindowConfig]:
    mb_cfg = load_mb_config(
        dotenv_path=args.env_file,
        verbose=args.verbose,
    )

    cfg = WindowConfig.from_mb_config(mb_cfg)

    cfg.print_cfg()
    cfg.log_cfg(logger)

    scans_path = mb_cfg.get_path("MB_SCANS", must_exist=False)
    logger.info("MB_SCANS = %s", scans_path)

    return mb_cfg, cfg



def log_open_tos_windows(logger: logging.Logger) -> None:
    all_titles = [t.strip() for t in gw.getAllTitles() if t.strip()]

    logger.info("Open windows containing 'think' or 'swim':")
    for title in all_titles:
        title_lower = title.lower()
        if "think" in title_lower or "swim" in title_lower:
            logger.info("  %r", title)



def load_and_refresh_widget_stacks(
    cfg: WindowConfig,
    logger: logging.Logger,
):
    widget_stacks = load_widget_layout(
        cfg.WIDGET_STACK_YAML,
        cfg.title_map,
    )

    update_root_window_positions(
        widget_stacks,
        cfg.title_map,
        logger,
        size_tolerance=4,
    )

    return widget_stacks



def choose_selected_widget(
    args: argparse.Namespace,
    widget_stacks,
) -> str | None:
    if not args.widgets:
        selected_widget = run_widget_selection_dialog(list(widget_stacks.keys()))
        if not selected_widget:
            print("No widget selected. Exiting.")
            return None
        return selected_widget

    selected_widget = args.widgets[0]

    if selected_widget not in widget_stacks:
        print(f"Invalid widget name: {selected_widget}")
        return None

    selected_msg = f"selected_widget: {selected_widget!r}"
    print()
    print("-" * 18)
    print(f"| {selected_msg}")
    print("-" * 18)

    return selected_widget



def prepare_window_for_widget(
    selected_widget: str,
    widget_stacks,
    cfg: WindowConfig,
    logger: logging.Logger,
) -> None:
    if is_window_visible(selected_widget, widget_stacks, cfg.title_map):
        bring_window_to_front(selected_widget, widget_stacks, cfg.title_map)
    else:
        msg = (
            f"⚠️  Warning: Window for widget {selected_widget!r} "
            "is not visible. Monitoring will continue."
        )
        print(msg)
        logger.warning(msg)



def start_dynamic_monitor(widget_stacks, logger: logging.Logger) -> threading.Thread:
    supervisor = threading.Thread(
        target=dynamic_window_monitor,
        args=(widget_stacks, logger),
        daemon=True,
    )
    supervisor.start()
    return supervisor



def wait_for_pose_trigger(logger: logging.Logger) -> None:
    logger.info("Waiting for pose trigger (Ctrl+Shift+J)...")
    print("\nWaiting for pose trigger (Ctrl+Shift+J)...")

    while not is_ctrl_shift_j_pressed():
        time.sleep(0.1)



def capture_selected_widget(
    selected_widget: str,
    widget_stacks,
    cfg: WindowConfig,
    args: argparse.Namespace,
    logger: logging.Logger,
) -> None:
    if not is_window_visible(selected_widget, widget_stacks, cfg.title_map):
        logger.error(
            "❌ Cannot trigger pose: Window for widget %r is still not visible.",
            selected_widget,
        )
        sys.exit(1)

    logger.info("✅ Pose triggered. Bringing window to front and waiting 5 seconds...")
    bring_window_to_front(selected_widget, widget_stacks, cfg.title_map)

    update_root_window_positions(
        widget_stacks,
        cfg.title_map,
        logger,
        size_tolerance=4,
    )

    print("✅ Pose triggered. Window brought to front.")
    print("⏳ Waiting 5 seconds before screenshot...")

    time.sleep(5)

    bring_window_to_front(selected_widget, widget_stacks, cfg.title_map)

    # Critical refresh immediately before capture.
    update_root_window_positions(
        widget_stacks,
        cfg.title_map,
        logger,
        size_tolerance=4,
    )

    logger.info("📸 Capturing screenshot now.")

    capture_paths = draw_widget_bounds_filtered(
        widget_stacks,
        [selected_widget],
        logger,
        capture_dir="captures",
        yaml_path=str(cfg.WIDGET_STACK_YAML),
        save_raw=not args.no_raw_capture,
        show_image=True,
    )

    logger.info("Capture files:")
    for label, path in capture_paths.items():
        logger.info("  %s: %s", label, path)


def run_main(logger: logging.Logger) -> None:
    parser = build_parser()
    args = parser.parse_args()

    _mb_cfg, cfg = load_runtime_config(args, logger)

    log_open_tos_windows(logger)

    widget_stacks = load_and_refresh_widget_stacks(cfg, logger)

    selected_widget = choose_selected_widget(args, widget_stacks)
    if selected_widget is None:
        return

    logger.info("--->> selected_widget: %r", selected_widget)

    prepare_window_for_widget(selected_widget, widget_stacks, cfg, logger)

    start_dynamic_monitor(widget_stacks, logger)

    wait_for_pose_trigger(logger)

    capture_selected_widget(
        selected_widget,
        widget_stacks,
        cfg,
        args,
        logger,
    )



if __name__ == "__main__":

    from logger import setup_logger
    logger = setup_logger()

    run_main(logger)
