# window_config.py
"""
ToS-specific window configuration.

This module does not load .env files directly. General MB_* configuration
loading is handled by:

    mb_tools.config.load_mb_config()

This module validates the MB_* values needed by the ToS GUI survey tools and
organizes them into a small WindowConfig object.

Important naming distinction:

    YAML root widget names:
        win_main
        win_wl_symbols_import
        etc.

    MB_* config variable names:
        MB_WINDOW_TOS_MAIN
        MB_WINDOW_TOS_WL_SYMBOLS
        etc.

    OS window title prefixes:
        Main@thinkorswim
        Symbols Import
        etc.

ROOT_TITLE_KEY_MAP is the one intentional bridge between YAML root names and
MB_* window-title configuration keys.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mb_tools.config import MBConfig


# Map YAML root pseudo-widget names to the MB_* key that supplies the
# corresponding OS window title prefix.
ROOT_TITLE_KEY_MAP: dict[str, str] = {
    "win_main": "MB_WINDOW_TOS_MAIN",
    "win_logon": "MB_WINDOW_TOS_LOGON",
    "win_updater": "MB_WINDOW_TOS_UPDATE",
    "win_export": "MB_WINDOW_TOS_EXPORT",
    "win_wl_main": "MB_WINDOW_TOS_WL_MAIN",
    "win_wl_export": "MB_WINDOW_TOS_WL_EXPORT",
    "win_wl_symbols_import": "MB_WINDOW_TOS_WL_SYMBOLS",
}


REQUIRED_WINDOW_KEYS: list[str] = [
    "MB_WINDOW_TOS",
    *ROOT_TITLE_KEY_MAP.values(),
]


REQUIRED_PATH_KEYS: list[str] = [
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
    Optionally raises FileNotFoundError if must_exist=True and a path does not
    exist.
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

    window_tos: str
    title_map: dict[str, str]
    pwidget_yaml: Path

    @property
    def WINDOW_TOS(self) -> str:
        """
        Backward-compatible alias.

        Prefer window_tos in new code.
        """
        return self.window_tos

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
            mb_cfg: Result from mb_tools.config.load_mb_config().
            require_yaml_exists: If True, MB_PWIDGET_YAML must point to an
                existing file.

        Raises:
            RuntimeError: If required MB_* values are missing or blank.
            FileNotFoundError: If require_yaml_exists=True and MB_PWIDGET_YAML
                does not exist.
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
                "MB_PWIDGET_YAML resolved to a path that is not a file: "
                f"{yaml_path}"
            )

        title_map = {
            root_name: window_values[mb_key]
            for root_name, mb_key in ROOT_TITLE_KEY_MAP.items()
        }

        return cls(
            window_tos=window_values["MB_WINDOW_TOS"],
            title_map=title_map,
            pwidget_yaml=yaml_path,
        )

    def print_cfg(self) -> None:
        """Print resolved ToS window configuration."""
        print("Window configuration:")
        print(f"  MB_PWIDGET_YAML      = {self.pwidget_yaml}")
        print(f"  MB_WINDOW_TOS        = {self.window_tos!r}")

        for root_name, mb_key in ROOT_TITLE_KEY_MAP.items():
            print(f"  {mb_key:<24} = {self.title_map[root_name]!r}")

    def log_cfg(self, logger) -> None:
        """Log resolved ToS window configuration."""
        logger.info("Window configuration:")
        logger.info("  MB_PWIDGET_YAML      = %s", self.pwidget_yaml)
        logger.info("  MB_WINDOW_TOS        = %r", self.window_tos)

        for root_name, mb_key in ROOT_TITLE_KEY_MAP.items():
            logger.info("  %-24s = %r", mb_key, self.title_map[root_name])
