# # drawing.py

# from __future__ import annotations

# import json
# from datetime import datetime
# from pathlib import Path
# from typing import Dict, List

# import cv2
# import numpy as np
# import pyautogui

# from mb_tools.pseudo_widgets import WidgetStack


# COLOR_PALETTE = [
#     (192, 255, 192),  # Green
#     (255, 192, 192),  # Blue
#     (192, 192, 255),  # Red
#     (255, 255, 192),  # Yellow
#     (255, 192, 255),  # Magenta
#     (192, 165, 255),  # Orange
# ]


# def _stack_display_name(stack: WidgetStack) -> str:
#     """
#     Return the leaf name for a WidgetStack.

#     This avoids direct stack.name access, which some linters may not recognize
#     when WidgetStack is imported from mb_tools.
#     """
#     return stack.path.split("/")[-1]


# def _safe_filename_part(text: str) -> str:
#     """
#     Make a string safer for use in a filename.
#     """
#     cleaned = text.strip().replace("\\", "_").replace("/", "_")
#     cleaned = cleaned.replace(":", "-").replace("*", "_").replace("?", "_")
#     cleaned = cleaned.replace('"', "_").replace("<", "_").replace(">", "_")
#     cleaned = cleaned.replace("|", "_").replace(" ", "_")
#     return cleaned or "unnamed"


# def _yaml_version_from_path(yaml_path: str | Path | None) -> str | None:
#     """
#     Derive a simple YAML version string from the filename.

#     Example:
#         layout_scanner3_v1p0.yaml -> scanner3_v1p0
#     """
#     if yaml_path is None:
#         return None

#     stem = Path(yaml_path).stem

#     if stem.startswith("layout_"):
#         return stem.removeprefix("layout_")

#     return stem


# def _region_metadata(stack: WidgetStack) -> dict[str, object]:
#     """
#     Build metadata for one widget stack node.
#     """
#     region = stack.absolute_region()

#     return {
#         "name": _stack_display_name(stack),
#         "path": stack.path,
#         "coord": stack.coord,
#         "x_tl": region.x_tl,
#         "y_tl": region.y_tl,
#         "width": region.width,
#         "height": region.height,
#         "x_center": region.x_tl + region.width / 2,
#         "y_center": region.y_tl + region.height / 2,
#         "level": len(stack.ancestry()) - 1,
#     }


# def _build_capture_paths(
#     *,
#     capture_dir: str | Path,
#     selected_widget: str,
#     timestamp: datetime,
# ) -> dict[str, Path]:
#     """
#     Build output paths for raw image, annotated image, and metadata.
#     """
#     capture_dir = Path(capture_dir)
#     capture_dir.mkdir(parents=True, exist_ok=True)

#     stamp = timestamp.strftime("%Y-%m-%d-%H-%M-%S")
#     widget_part = _safe_filename_part(selected_widget)
#     base = f"pwidget-{stamp}-{widget_part}"

#     return {
#         "raw": capture_dir / f"{base}-raw.png",
#         "annotated": capture_dir / f"{base}-annotated.png",
#         "metadata": capture_dir / f"{base}-metadata.json",
#     }


# def draw_depth_legend(
#     img,
#     levels_in_use: list[int],
#     x: int = 20,
# ) -> None:
#     """
#     Draw a depth/color legend on the left side of the image, centered vertically.
#     """
#     if not levels_in_use:
#         return

#     levels_in_use = sorted(set(levels_in_use))

#     row_h = 26
#     swatch_size = 16
#     padding = 12
#     text_x_offset = 30
#     legend_w = 180
#     legend_h = padding * 2 + len(levels_in_use) * row_h

#     img_h, _img_w = img.shape[:2]
#     y = max(10, (img_h - legend_h) // 2)

#     # Background box
#     cv2.rectangle(
#         img,
#         (x, y),
#         (x + legend_w, y + legend_h),
#         (40, 40, 40),
#         -1,
#     )

#     # Border
#     cv2.rectangle(
#         img,
#         (x, y),
#         (x + legend_w, y + legend_h),
#         (200, 200, 200),
#         1,
#     )

#     # Title
#     cv2.putText(
#         img,
#         "Widget Depth",
#         (x + padding, y + 18),
#         cv2.FONT_HERSHEY_SIMPLEX,
#         0.5,
#         (255, 255, 255),
#         1,
#     )

#     # Entries
#     start_y = y + padding + 24

#     for level in levels_in_use:
#         color = COLOR_PALETTE[level % len(COLOR_PALETTE)]
#         row_y = start_y + level * row_h

#         cv2.rectangle(
#             img,
#             (x + padding, row_y - swatch_size + 4),
#             (x + padding + swatch_size, row_y + 4),
#             color,
#             -1,
#         )

#         cv2.putText(
#             img,
#             f"Level {level}",
#             (x + padding + text_x_offset, row_y),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.5,
#             (255, 255, 255),
#             1,
#         )


# def draw_widget_bounds_filtered(
#     widget_stacks: Dict[str, WidgetStack],
#     widget_names: List[str],
#     logger,
#     *,
#     capture_dir: str | Path = "captures",
#     yaml_path: str | Path | None = None,
#     save_raw: bool = True,
#     show_image: bool = True,
# ) -> dict[str, Path]:
#     """
#     Draw bounds for selected widgets and their ancestors.

#     Saves:
#         - annotated screenshot
#         - optional raw screenshot
#         - metadata JSON sidecar file

#     Returns
#     -------
#     dict[str, Path]
#         Paths for files that were created.
#     """
#     if not widget_names:
#         raise ValueError("At least one widget name is required.")

#     primary_widget = widget_names[0]
#     timestamp = datetime.now()

#     paths = _build_capture_paths(
#         capture_dir=capture_dir,
#         selected_widget=primary_widget,
#         timestamp=timestamp,
#     )

#     ordered_stacks: list[WidgetStack] = []
#     seen_paths: set[str] = set()
#     selected_set = set(widget_names)

#     for name in widget_names:
#         if name not in widget_stacks:
#             logger.warning("Requested widget %r not found in widget_stacks.", name)
#             continue

#         path: list[WidgetStack] = []
#         current = widget_stacks[name]

#         while current is not None:
#             path.append(current)
#             current = current.parent

#         path.reverse()

#         for stack in path:
#             stack_key = stack.path

#             if stack_key not in seen_paths:
#                 ordered_stacks.append(stack)
#                 seen_paths.add(stack_key)

#     screenshot = pyautogui.screenshot()
#     raw_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
#     annotated_img = raw_img.copy()

#     if save_raw:
#         cv2.imwrite(str(paths["raw"]), raw_img)
#         logger.info("Saved raw screenshot: %s", paths["raw"])

#     levels_used: list[int] = []
#     drawn_widgets: list[dict[str, object]] = []

#     # Draw ancestors / non-selected widgets first.
#     for stack in ordered_stacks:
#         name = _stack_display_name(stack)

#         if name in selected_set:
#             continue

#         region = stack.absolute_region()
#         x, y = region.x_tl, region.y_tl
#         w, h = region.width, region.height

#         level = len(stack.ancestry()) - 1
#         levels_used.append(level)

#         color = COLOR_PALETTE[level % len(COLOR_PALETTE)]

#         cv2.rectangle(annotated_img, (x, y), (x + w, y + h), color, 1)

#         cv2.putText(
#             annotated_img,
#             name,
#             (x, y - 5),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.5,
#             color,
#             1,
#         )

#         cv2.circle(
#             annotated_img,
#             (x + w // 2, y + h // 2),
#             4,
#             (0, 0, 255),
#             -1,
#         )

#         metadata = _region_metadata(stack)
#         metadata["selected"] = False
#         drawn_widgets.append(metadata)

#         logger.info("%s at (%s,%s) size %sx%s level=%s", name, x, y, w, h, level)

#     # Draw selected widgets last.
#     for name in widget_names:
#         if name not in widget_stacks:
#             continue

#         stack = widget_stacks[name]

#         region = stack.absolute_region()
#         x, y = region.x_tl, region.y_tl
#         w, h = region.width, region.height

#         level = len(stack.ancestry()) - 1
#         levels_used.append(level)

#         color = COLOR_PALETTE[level % len(COLOR_PALETTE)]

#         cv2.rectangle(annotated_img, (x, y), (x + w, y + h), color, 1)

#         cv2.putText(
#             annotated_img,
#             name,
#             (x, y - 5),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.5,
#             color,
#             1,
#         )

#         cv2.circle(
#             annotated_img,
#             (x + w // 2, y + h // 2),
#             4,
#             (0, 0, 255),
#             -1,
#         )

#         metadata = _region_metadata(stack)
#         metadata["selected"] = True
#         drawn_widgets.append(metadata)

#         logger.info(
#             "%s at (%s,%s) size %sx%s level=%s [SELECTED]",
#             name,
#             x,
#             y,
#             w,
#             h,
#             level,
#         )

#     draw_depth_legend(annotated_img, levels_used, x=20)

#     cv2.imwrite(str(paths["annotated"]), annotated_img)
#     logger.info("Saved annotated screenshot: %s", paths["annotated"])

#     metadata_doc = {
#         "capture_timestamp": timestamp.isoformat(timespec="seconds"),
#         "selected_widgets": widget_names,
#         "primary_selected_widget": primary_widget,
#         "yaml_path": str(yaml_path) if yaml_path is not None else None,
#         "yaml_version": _yaml_version_from_path(yaml_path),
#         "raw_screenshot": str(paths["raw"]) if save_raw else None,
#         "annotated_screenshot": str(paths["annotated"]),
#         "drawn_widgets": drawn_widgets,
#     }

#     with paths["metadata"].open("w", encoding="utf-8") as f:
#         json.dump(metadata_doc, f, indent=2)

#     logger.info("Saved capture metadata: %s", paths["metadata"])

#     if show_image:
#         cv2.imshow("Filtered Widget Bounds", annotated_img)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()

#     saved_paths = {
#         "annotated": paths["annotated"],
#         "metadata": paths["metadata"],
#     }

#     if save_raw:
#         saved_paths["raw"] = paths["raw"]

#     return saved_paths






# drawing.py

"""
Screenshot capture and pseudo-widget annotation helpers.

This module is still local to ToS_gui_survey. It depends on the reusable
pseudo-widget model from mb_tools, but the capture naming, metadata, and
display behavior are project-specific for now.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import cv2
import numpy as np
import pyautogui

from mb_tools.pseudo_widgets import WidgetStack


COLOR_PALETTE = [
    (192, 255, 192),  # Green
    (255, 192, 192),  # Blue
    (192, 192, 255),  # Red
    (255, 255, 192),  # Yellow
    (255, 192, 255),  # Magenta
    (192, 165, 255),  # Orange
]


def _stack_display_name(stack: WidgetStack) -> str:
    """
    Return the leaf name for a WidgetStack.

    This avoids direct stack.name access, which some linters may not recognize
    when WidgetStack is imported from mb_tools.
    """
    return stack.path.split("/")[-1]


def _safe_filename_part(text: str) -> str:
    """
    Make a string safer for use in a filename.
    """
    cleaned = text.strip().replace("\\", "_").replace("/", "_")
    cleaned = cleaned.replace(":", "-").replace("*", "_").replace("?", "_")
    cleaned = cleaned.replace('"', "_").replace("<", "_").replace(">", "_")
    cleaned = cleaned.replace("|", "_").replace(" ", "_")
    return cleaned or "unnamed"


def _yaml_version_from_path(yaml_path: str | Path | None) -> str | None:
    """
    Derive a simple YAML version string from the filename.

    Example:
        layout_scanner3_v1p0.yaml -> scanner3_v1p0
    """
    if yaml_path is None:
        return None

    stem = Path(yaml_path).stem

    if stem.startswith("layout_"):
        return stem.removeprefix("layout_")

    return stem


def _region_metadata(stack: WidgetStack) -> dict[str, object]:
    """
    Build metadata for one widget stack node.
    """
    region = stack.absolute_region()

    return {
        "name": _stack_display_name(stack),
        "path": stack.path,
        "coord": stack.coord,
        "x_tl": region.x_tl,
        "y_tl": region.y_tl,
        "width": region.width,
        "height": region.height,
        "x_center": region.x_tl + region.width / 2,
        "y_center": region.y_tl + region.height / 2,
        "level": len(stack.ancestry()) - 1,
    }


def _build_capture_paths(
    *,
    capture_dir: str | Path,
    selected_widget: str,
    timestamp: datetime,
) -> dict[str, Path]:
    """
    Build output paths for raw image, annotated image, and metadata.
    """
    capture_dir = Path(capture_dir)
    capture_dir.mkdir(parents=True, exist_ok=True)

    stamp = timestamp.strftime("%Y-%m-%d-%H-%M-%S")
    widget_part = _safe_filename_part(selected_widget)
    base = f"pwidget-{stamp}-{widget_part}"

    return {
        "raw": capture_dir / f"{base}-raw.png",
        "annotated": capture_dir / f"{base}-annotated.png",
        "metadata": capture_dir / f"{base}-metadata.json",
    }


def _capture_screen_bgr() -> np.ndarray:
    """
    Capture the full screen and return an OpenCV BGR image.
    """
    screenshot = pyautogui.screenshot()
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)


def _collect_ordered_stacks(
    widget_stacks: Dict[str, WidgetStack],
    widget_names: List[str],
    logger: logging.Logger,
) -> list[WidgetStack]:
    """
    Collect selected widgets and their ancestors in root-to-leaf order.

    Duplicate stack paths are included only once.
    """
    ordered_stacks: list[WidgetStack] = []
    seen_paths: set[str] = set()

    for name in widget_names:
        if name not in widget_stacks:
            logger.warning("Requested widget %r not found in widget_stacks.", name)
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

    return ordered_stacks



def _safe_label_origin(
    img: np.ndarray,
    text: str,
    preferred_x: int,
    preferred_y: int,
    *,
    font_face: int = cv2.FONT_HERSHEY_SIMPLEX,
    font_scale: float = 0.5,
    thickness: int = 1,
    margin: int = 4,
) -> tuple[int, int]:
    """
    Return a text origin that keeps the rendered label inside the image.

    OpenCV putText() uses the supplied point as the lower-left baseline
    of the text, not the top-left corner.
    """
    img_h, img_w = img.shape[:2]

    (text_w, text_h), baseline = cv2.getTextSize(
        text,
        font_face,
        font_scale,
        thickness,
    )

    # Clamp X so the full label width remains visible.
    x = max(margin, min(preferred_x, img_w - text_w - margin))

    # Clamp Y baseline so the label's top and bottom remain visible.
    min_y = text_h + margin
    max_y = img_h - baseline - margin
    y = max(min_y, min(preferred_y, max_y))

    return x, y



def _draw_one_widget(
    annotated_img: np.ndarray,
    stack: WidgetStack,
    *,
    selected: bool,
    logger: logging.Logger,
) -> tuple[int, dict[str, object]]:
    """
    Draw one pseudo-widget and return its level and metadata.

    Selected and non-selected widgets intentionally use the same visual style.
    The selected state is still recorded in metadata and logs.
    """
    name = _stack_display_name(stack)
    region = stack.absolute_region()

    x = region.x_tl
    y = region.y_tl
    w = region.width
    h = region.height

    level = len(stack.ancestry()) - 1
    color = COLOR_PALETTE[level % len(COLOR_PALETTE)]

    cv2.rectangle(
        annotated_img,
        (x, y),
        (x + w, y + h),
        color,
        1,
    )

    # cv2.putText(
    #     annotated_img,
    #     name,
    #     (x, y - 5),
    #     cv2.FONT_HERSHEY_SIMPLEX,
    #     0.5,
    #     color,
    #     1,
    # )




    font_face = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1

    preferred_label_x = x
    preferred_label_y = y - 5

    # If label would be above the image, place it just below the widget box.
    if preferred_label_y < 12:
        preferred_label_y = y + h + 14

    label_x, label_y = _safe_label_origin(
        annotated_img,
        name,
        preferred_label_x,
        preferred_label_y,
        font_face=font_face,
        font_scale=font_scale,
        thickness=font_thickness,
    )

    cv2.putText(
        annotated_img,
        name,
        (label_x, label_y),
        font_face,
        font_scale,
        color,
        font_thickness,
)




    cv2.circle(
        annotated_img,
        (x + w // 2, y + h // 2),
        4,
        (0, 0, 255),
        -1,
    )

    metadata = _region_metadata(stack)
    metadata["selected"] = selected

    if selected:
        logger.info(
            "%s at (%s,%s) size %sx%s level=%s [SELECTED]",
            name,
            x,
            y,
            w,
            h,
            level,
        )
    else:
        logger.info(
            "%s at (%s,%s) size %sx%s level=%s",
            name,
            x,
            y,
            w,
            h,
            level,
        )

    return level, metadata


def _draw_stack_annotations(
    annotated_img: np.ndarray,
    ordered_stacks: list[WidgetStack],
    widget_stacks: Dict[str, WidgetStack],
    widget_names: List[str],
    logger: logging.Logger,
) -> tuple[list[int], list[dict[str, object]]]:
    """
    Draw ancestor widgets first, then selected widgets last.

    The selected widgets are drawn last so they remain visible if rectangles
    overlap, but they no longer use thicker lines or larger fonts.
    """
    selected_set = set(widget_names)

    levels_used: list[int] = []
    drawn_widgets: list[dict[str, object]] = []

    # Draw ancestors / non-selected widgets first.
    for stack in ordered_stacks:
        name = _stack_display_name(stack)
        if name in selected_set:
            continue

        level, metadata = _draw_one_widget(
            annotated_img,
            stack,
            selected=False,
            logger=logger,
        )

        levels_used.append(level)
        drawn_widgets.append(metadata)

    # Draw selected widgets last.
    for name in widget_names:
        if name not in widget_stacks:
            continue

        stack = widget_stacks[name]

        level, metadata = _draw_one_widget(
            annotated_img,
            stack,
            selected=True,
            logger=logger,
        )

        levels_used.append(level)
        drawn_widgets.append(metadata)

    return levels_used, drawn_widgets


def draw_depth_legend(
    img: np.ndarray,
    levels_in_use: list[int],
    x: int = 20,
) -> None:
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

    img_h, _img_w = img.shape[:2]
    y = max(10, (img_h - legend_h) // 2)

    # Background box
    cv2.rectangle(
        img,
        (x, y),
        (x + legend_w, y + legend_h),
        (40, 40, 40),
        -1,
    )

    # Border
    cv2.rectangle(
        img,
        (x, y),
        (x + legend_w, y + legend_h),
        (200, 200, 200),
        1,
    )

    # Title
    cv2.putText(
        img,
        "Widget Depth",
        (x + padding, y + 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
    )

    start_y = y + padding + 24

    for index, level in enumerate(levels_in_use):
        color = COLOR_PALETTE[level % len(COLOR_PALETTE)]
        row_y = start_y + index * row_h

        cv2.rectangle(
            img,
            (x + padding, row_y - swatch_size + 4),
            (x + padding + swatch_size, row_y + 4),
            color,
            -1,
        )

        cv2.putText(
            img,
            f"Level {level}",
            (x + padding + text_x_offset, row_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )


def _write_metadata(
    metadata_path: Path,
    *,
    timestamp: datetime,
    widget_names: List[str],
    primary_widget: str,
    yaml_path: str | Path | None,
    save_raw: bool,
    paths: dict[str, Path],
    drawn_widgets: list[dict[str, object]],
    logger: logging.Logger,
) -> None:
    """
    Write JSON sidecar metadata for the capture.
    """
    metadata_doc = {
        "capture_timestamp": timestamp.isoformat(timespec="seconds"),
        "selected_widgets": widget_names,
        "primary_selected_widget": primary_widget,
        "yaml_path": str(yaml_path) if yaml_path is not None else None,
        "yaml_version": _yaml_version_from_path(yaml_path),
        "raw_screenshot": str(paths["raw"]) if save_raw else None,
        "annotated_screenshot": str(paths["annotated"]),
        "drawn_widgets": drawn_widgets,
    }

    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(metadata_doc, f, indent=2)

    logger.info("Saved capture metadata: %s", metadata_path)


def _show_image(window_title: str, img: np.ndarray) -> None:
    """
    Display an image in an OpenCV window.
    """
    cv2.imshow(window_title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def draw_widget_bounds_filtered(
    widget_stacks: Dict[str, WidgetStack],
    widget_names: List[str],
    logger: logging.Logger,
    *,
    capture_dir: str | Path = "captures",
    yaml_path: str | Path | None = None,
    save_raw: bool = True,
    show_image: bool = True,
) -> dict[str, Path]:
    """
    Draw bounds for selected widgets and their ancestors.

    Saves:
        - annotated screenshot
        - optional raw screenshot
        - metadata JSON sidecar file

    Returns:
        dict[str, Path]
            Paths for files that were created.
    """
    if not widget_names:
        raise ValueError("At least one widget name is required.")

    primary_widget = widget_names[0]
    timestamp = datetime.now()

    paths = _build_capture_paths(
        capture_dir=capture_dir,
        selected_widget=primary_widget,
        timestamp=timestamp,
    )

    ordered_stacks = _collect_ordered_stacks(
        widget_stacks,
        widget_names,
        logger,
    )

    raw_img = _capture_screen_bgr()
    annotated_img = raw_img.copy()

    if save_raw:
        cv2.imwrite(str(paths["raw"]), raw_img)
        logger.info("Saved raw screenshot: %s", paths["raw"])

    levels_used, drawn_widgets = _draw_stack_annotations(
        annotated_img,
        ordered_stacks,
        widget_stacks,
        widget_names,
        logger,
    )

    draw_depth_legend(
        annotated_img,
        levels_used,
        x=20,
    )

    cv2.imwrite(str(paths["annotated"]), annotated_img)
    logger.info("Saved annotated screenshot: %s", paths["annotated"])

    _write_metadata(
        paths["metadata"],
        timestamp=timestamp,
        widget_names=widget_names,
        primary_widget=primary_widget,
        yaml_path=yaml_path,
        save_raw=save_raw,
        paths=paths,
        drawn_widgets=drawn_widgets,
        logger=logger,
    )

    if show_image:
        _show_image("Filtered Widget Bounds", annotated_img)

    saved_paths = {
        "annotated": paths["annotated"],
        "metadata": paths["metadata"],
    }

    if save_raw:
        saved_paths["raw"] = paths["raw"]

    return saved_paths
