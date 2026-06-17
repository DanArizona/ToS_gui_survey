# window_config.py

"""
ToS-specific window configuration.

This module does not load .env files directly.

General MB_* configuration loading is handled by:

    mb_tools.config.load_mb_config()

This module validates the MB_* values needed by the ToS GUI survey tools
and organizes them into a small WindowConfig object.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mb_tools.config import MBConfig


REQUIRED_WINDOW_KEYS = [
    "MB_WINDOW_TOS",
    "MB_WINDOW_TOS_MAIN",
    "MB_WINDOW_TOS_UPDATE",
    "MB_WINDOW_TOS_LOGON",
    "MB_WINDOW_TOS_EXPORT",
    "MB_WINDOW_TOS_WL_MAIN",
    "MB_WINDOW_TOS_WL_EXPORT",
    "MB_WINDOW_TOS_WL_SYMBOLS",
]


REQUIRED_PATH_KEYS = [
    "MB_PWIDGET_YAML",
]


def require_strs(mb_cfg: MBConfig, keys: list[str]) -> dict[str, str]:
    """
    Return required string values from MBConfig.

    Raises RuntimeError if any required values are missing or blank.
    """
    values: dict[str, str] = {}
    missing: list[str] = []

    for key in keys:
        value = mb_cfg.get(key)

        if value is None or not value.strip():
            missing.append(key)
        else:
            values[key] = value

    if missing:
        missing_text = "\n".join(f"  {key}" for key in missing)
        raise RuntimeError(
            "Missing required MB_* configuration variable(s):\n"
            f"{missing_text}"
        )

    return values


def require_paths(
    mb_cfg: MBConfig,
    keys: list[str],
    *,
    must_exist: bool = False,
) -> dict[str, Path]:
    """
    Return required path values from MBConfig.

    Raises RuntimeError if any required paths are missing or blank.
    Optionally raises FileNotFoundError if must_exist=True and a path does not exist.
    """
    values: dict[str, Path] = {}
    missing: list[str] = []

    for key in keys:
        raw_value = mb_cfg.get(key)

        if raw_value is None or not raw_value.strip():
            missing.append(key)
            continue

        path = Path(raw_value).expanduser().resolve()

        if must_exist and not path.exists():
            raise FileNotFoundError(
                f"{key} resolved to a non-existent path: {path}"
            )

        values[key] = path

    if missing:
        missing_text = "\n".join(f"  {key}" for key in missing)
        raise RuntimeError(
            "Missing required MB_* path configuration variable(s):\n"
            f"{missing_text}"
        )

    return values


@dataclass(frozen=True)
class WindowConfig:
    """
    Validated ToS window configuration.

    Values are loaded from MBConfig, not hard-coded here.
    """

    WINDOW_TOS: str
    WINDOW_TOS_MAIN: str
    WINDOW_TOS_UPDATE: str
    WINDOW_TOS_LOGON: str
    WINDOW_TOS_EXPORT: str
    WINDOW_TOS_WL_MAIN: str
    WINDOW_TOS_WL_EXPORT: str
    WINDOW_TOS_WL_SYMBOLS: str
    WIDGET_STACK_YAML: Path

    @property
    def title_map(self) -> dict[str, str]:
        """
        Map pseudo-widget YAML root names to actual OS window titles.
        """
        return {
            "win_main": self.WINDOW_TOS_MAIN,
            "win_logon": self.WINDOW_TOS_LOGON,
            "win_updater": self.WINDOW_TOS_UPDATE,
            "win_export": self.WINDOW_TOS_EXPORT,
            "win_wl_main": self.WINDOW_TOS_WL_MAIN,
            "win_wl_export": self.WINDOW_TOS_WL_EXPORT,
            "win_wl_symbols_import": self.WINDOW_TOS_WL_SYMBOLS,
        }

    @classmethod
    def from_mb_config(
        cls,
        mb_cfg: MBConfig,
        *,
        require_yaml_exists: bool = True,
    ) -> "WindowConfig":
        """
        Build a WindowConfig from an already-loaded MBConfig.

        Args:
            mb_cfg:
                Result from mb_tools.config.load_mb_config().

            require_yaml_exists:
                If True, MB_PWIDGET_YAML must point to an existing file.

        Raises:
            RuntimeError:
                If required MB_* values are missing or blank.

            FileNotFoundError:
                If require_yaml_exists=True and MB_PWIDGET_YAML does not exist.
        """
        window_values = require_strs(mb_cfg, REQUIRED_WINDOW_KEYS)

        path_values = require_paths(
            mb_cfg,
            REQUIRED_PATH_KEYS,
            must_exist=require_yaml_exists,
        )

        yaml_path = path_values["MB_PWIDGET_YAML"]

        if require_yaml_exists and not yaml_path.is_file():
            raise FileNotFoundError(
                f"MB_PWIDGET_YAML resolved to a path that is not a file: {yaml_path}"
            )

        return cls(
            WINDOW_TOS=window_values["MB_WINDOW_TOS"],
            WINDOW_TOS_MAIN=window_values["MB_WINDOW_TOS_MAIN"],
            WINDOW_TOS_UPDATE=window_values["MB_WINDOW_TOS_UPDATE"],
            WINDOW_TOS_LOGON=window_values["MB_WINDOW_TOS_LOGON"],
            WINDOW_TOS_EXPORT=window_values["MB_WINDOW_TOS_EXPORT"],
            WINDOW_TOS_WL_MAIN=window_values["MB_WINDOW_TOS_WL_MAIN"],
            WINDOW_TOS_WL_EXPORT=window_values["MB_WINDOW_TOS_WL_EXPORT"],
            WINDOW_TOS_WL_SYMBOLS=window_values["MB_WINDOW_TOS_WL_SYMBOLS"],
            WIDGET_STACK_YAML=yaml_path,
        )

    def print_cfg(self) -> None:
        """
        Print resolved ToS window configuration.
        """
        print("Window configuration:")
        print(f"  WIDGET_STACK_YAML      = {self.WIDGET_STACK_YAML}")
        print(f"  WINDOW_TOS             = {self.WINDOW_TOS!r}")
        print(f"  WINDOW_TOS_MAIN        = {self.WINDOW_TOS_MAIN!r}")
        print(f"  WINDOW_TOS_UPDATE      = {self.WINDOW_TOS_UPDATE!r}")
        print(f"  WINDOW_TOS_LOGON       = {self.WINDOW_TOS_LOGON!r}")
        print(f"  WINDOW_TOS_EXPORT      = {self.WINDOW_TOS_EXPORT!r}")
        print(f"  WINDOW_TOS_WL_MAIN     = {self.WINDOW_TOS_WL_MAIN!r}")
        print(f"  WINDOW_TOS_WL_EXPORT   = {self.WINDOW_TOS_WL_EXPORT!r}")
        print(f"  WINDOW_TOS_WL_SYMBOLS  = {self.WINDOW_TOS_WL_SYMBOLS!r}")

    def log_cfg(self, logger) -> None:
        """
        Log resolved ToS window configuration.
        """
        logger.info("Window configuration:")
        logger.info("  WIDGET_STACK_YAML      = %s", self.WIDGET_STACK_YAML)
        logger.info("  WINDOW_TOS             = %r", self.WINDOW_TOS)
        logger.info("  WINDOW_TOS_MAIN        = %r", self.WINDOW_TOS_MAIN)
        logger.info("  WINDOW_TOS_UPDATE      = %r", self.WINDOW_TOS_UPDATE)
        logger.info("  WINDOW_TOS_LOGON       = %r", self.WINDOW_TOS_LOGON)
        logger.info("  WINDOW_TOS_EXPORT      = %r", self.WINDOW_TOS_EXPORT)
        logger.info("  WINDOW_TOS_WL_MAIN     = %r", self.WINDOW_TOS_WL_MAIN)
        logger.info("  WINDOW_TOS_WL_EXPORT   = %r", self.WINDOW_TOS_WL_EXPORT)
        logger.info("  WINDOW_TOS_WL_SYMBOLS  = %r", self.WINDOW_TOS_WL_SYMBOLS)
    