# drawing.py

import pyautogui
import numpy as np
import cv2
# import logging
from typing import Dict, List, Set
# from models import WidgetStack
from mb_tools.pseudo_widgets import WidgetStack
from utils import days_seconds_ytd


COLOR_PALETTE = [
    (192, 255, 192),     # Green
    (255, 192, 192),     # Blue
    (192, 192, 255),     # Red
    (255, 255, 192),     # Yellow
    (255, 192, 255),     # Magenta
    (192, 165, 255),     # Orange
]



def draw_depth_legend(
    img,
    levels_in_use: list[int],
    x: int = 20,
):
    """
    Draw a depth/color legend on the left side of the image, centered vertically.
    """
    if not levels_in_use:
        return

    levels_in_use = sorted(set(levels_in_use))

    row_h = 26
    swatch_size = 16
    padding = 12
    text_x_offset = 30

    legend_w = 180
    legend_h = padding * 2 + len(levels_in_use) * row_h

    img_h, img_w = img.shape[:2]
    y = max(10, (img_h - legend_h) // 2)

    # Background box
    cv2.rectangle(
        img,
        (x, y),
        (x + legend_w, y + legend_h),
        (40, 40, 40),
        -1
    )

    # Border
    cv2.rectangle(
        img,
        (x, y),
        (x + legend_w, y + legend_h),
        (200, 200, 200),
        1
    )

    # Title
    cv2.putText(
        img,
        "Widget Depth",
        (x + padding, y + 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1
    )

    # Entries
    start_y = y + padding + 24
    for i, level in enumerate(levels_in_use):
        color = COLOR_PALETTE[level % len(COLOR_PALETTE)]
        row_y = start_y + i * row_h

        # Color swatch
        cv2.rectangle(
            img,
            (x + padding, row_y - swatch_size + 4),
            (x + padding + swatch_size, row_y + 4),
            color,
            -1
        )

        # Label
        cv2.putText(
            img,
            f"Level {level}",
            (x + padding + text_x_offset, row_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )


# def draw_widget_bounds(widget_stacks: Dict[str, WidgetStack], window_title: str):
def draw_widget_bounds(
    widget_stacks: Dict[str, WidgetStack],
    window_title: str,
    logger):

    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    for stack in widget_stacks.values():
        # if stack.ancestry()[0] != window_title:
        #     continue
        if stack.root().path != window_title:
            continue


        # x, y = stack.get_absolute_position()
        # w, h = stack.bbox.width, stack.bbox.height
        # name = stack.bbox.name

        region = stack.absolute_region()
        x, y = region.x_tl, region.y_tl
        w, h = region.width, region.height
        # name = stack.name
        name = stack.path.split("/")[-1]



        level = len(stack.ancestry()) - 1
        color = COLOR_PALETTE[level % len(COLOR_PALETTE)]

        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        cv2.putText(img, name, (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        cv2.circle(img, (x + w // 2, y + h // 2), 4, (0, 0, 255), -1)

        logger.info(f"{name} at ({x},{y}) size {w}x{h}")

    cv2.imshow("Widget Bounds", img)
    cv2.waitKey(0)
    fname = "bounds_dbg_" + days_seconds_ytd() + ".png"
    cv2.imwrite(fname, img)
    cv2.destroyAllWindows()




def draw_widget_bounds_filtered(
    widget_stacks: Dict[str, WidgetStack],
    widget_names: List[str],
    logger,
):
    """
    Draw bounds for selected widgets and their ancestors.

    Behavior:
    - Ancestors are drawn first, so deeper widgets appear on top.
    - Colors depend on hierarchy depth.
    - Selected widget(s) are drawn last with thicker outlines.
    - A depth legend is drawn at the left-center of the screenshot.
    """

    # ordered_stacks: list[WidgetStack] = []
    # seen: set[WidgetStack] = set()
    # selected_set = set(widget_names)

    # for name in widget_names:
    #     if name not in widget_stacks:
    #         logger.warning(f"Requested widget '{name}' not found in widget_stacks.")
    #         continue

    #     path: list[WidgetStack] = []
    #     current = widget_stacks[name]
    #     while current:
    #         path.append(current)
    #         current = current.parent
    #     path.reverse()

    #     for stack in path:
    #         if stack not in seen:
    #             ordered_stacks.append(stack)
    #             seen.add(stack)

    ordered_stacks: list[WidgetStack] = []
    seen_paths: set[str] = set()
    selected_set = set(widget_names)

    for name in widget_names:
        if name not in widget_stacks:
            logger.warning(f"Requested widget '{name}' not found in widget_stacks.")
            continue

        path: list[WidgetStack] = []
        current = widget_stacks[name]

        while current is not None:
            path.append(current)
            current = current.parent

        path.reverse()

        for stack in path:
            stack_key = stack.path

            if stack_key not in seen_paths:
                ordered_stacks.append(stack)
                seen_paths.add(stack_key)

    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    levels_used: list[int] = []



    # Draw ancestors/non-selected first
    # for stack in ordered_stacks:
    #     name = stack.bbox.name
    #     if name in selected_set:
    #         continue

    #     x, y = stack.get_absolute_position()
    #     w, h = stack.bbox.width, stack.bbox.height
    for stack in ordered_stacks:
        name = stack.name
        if name in selected_set:
            continue



        region = stack.absolute_region()
        x, y = region.x_tl, region.y_tl
        w, h = region.width, region.height



        level = len(stack.ancestry()) - 1
        levels_used.append(level)
        color = COLOR_PALETTE[level % len(COLOR_PALETTE)]

        # cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 1)
        cv2.putText(
            img,
            name,
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1
        )
        cv2.circle(img, (x + w // 2, y + h // 2), 4, (0, 0, 255), -1)

        logger.info(f"{name} at ({x},{y}) size {w}x{h} level={level}")

    # Draw selected widget(s) last
    for name in widget_names:
        if name not in widget_stacks:
            continue



        # stack = widget_stacks[name]
        # x, y = stack.get_absolute_position()
        # w, h = stack.bbox.width, stack.bbox.height
        stack = widget_stacks[name]
        region = stack.absolute_region()
        x, y = region.x_tl, region.y_tl
        w, h = region.width, region.height



        level = len(stack.ancestry()) - 1
        levels_used.append(level)
        color = COLOR_PALETTE[level % len(COLOR_PALETTE)]

        # cv2.rectangle(img, (x, y), (x + w, y + h), color, 3)
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        cv2.putText(
            img,
            name,
            (x, y - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            # 0.5,
            color,
            2
        )
        cv2.circle(img, (x + w // 2, y + h // 2), 5, (0, 0, 255), -1)

        logger.info(f"{name} at ({x},{y}) size {w}x{h} level={level} [SELECTED]")

    # Add legend on left side, vertically centered
    draw_depth_legend(img, levels_used, x=20)

    cv2.imshow("Filtered Widget Bounds", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

