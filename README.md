# ToS GUI Survey

`ToS_gui_survey` is a Windows-based diagnostic tool for surveying and validating ThinkOrSwim GUI pseudo-widget layouts.

The program:

* loads a pseudo-widget hierarchy from a YAML layout file;
* associates YAML root widgets with live ThinkOrSwim windows;
* refreshes root-window positions from the current Windows desktop;
* lets the user select a pseudo-widget;
* waits for a keyboard trigger;
* captures the screen;
* draws the selected widget and its ancestor hierarchy;
* saves the capture and coordinate metadata for inspection.

This project depends on the reusable configuration, pseudo-widget, and window-management components in the companion `mb_tools` project.

## Platform

The current implementation is intended for:

* Windows 11
* Python 3.12
* ThinkOrSwim desktop
* a configured pseudo-widget YAML layout
* the `mb_tools` Python package

The program uses Windows-specific window and keyboard APIs and is not expected to run unchanged on Linux or macOS.

## Repository entry point

Run the project from the repository root using:

```cmd
python widget_check.py
```

The repository is currently a script-based project. It does not install a separate console command.

## Installation

### 1. Clone the repositories

The project expects both `ToS_gui_survey` and `mb_tools` to be available.

Example directory layout:

```text
C:\Users\<username>\Documents\github\
├── mb_tools
├── pwidget_layouts
└── ToS_gui_survey
```

### 2. Activate a Python environment

Example using Conda:

```cmd
conda activate sea-green
```

Python 3.12 is recommended.

### 3. Install `mb_tools`

For development, install the local `mb_tools` repository in editable mode:

```cmd
python -m pip install -e "C:\Users\<username>\Documents\github\mb_tools[qt]"
```

### 4. Install the remaining runtime dependencies

`ToS_gui_survey` does not currently contain its own `pyproject.toml` or `requirements.txt`.

Install the project-specific dependencies with:

```cmd
python -m pip install keyboard opencv-python numpy pyautogui pywin32
```

Verify the important imports:

```cmd
python -c "import cv2, keyboard, numpy, pyautogui, win32api; import mb_tools; print('Imports OK')"
```

## Configuration

The program loads `MB_*` configuration through `mb_tools.config.load_mb_config()`.

By default, it looks for a project `.env` file in the current directory:

```text
ToS_gui_survey\.env
```

The `.env` file is excluded from Git and should not be committed.

### Required configuration variables

The current program requires:

```dotenv
MB_PWIDGET_YAML=C:\path\to\layout_scanner.yaml

MB_WINDOW_TOS=thinkorswim
MB_WINDOW_TOS_MAIN=Main@thinkorswim
MB_WINDOW_TOS_LOGON=<ThinkOrSwim logon title prefix>
MB_WINDOW_TOS_UPDATE=<ThinkOrSwim updater title prefix>
MB_WINDOW_TOS_EXPORT=<ThinkOrSwim export-dialog title prefix>
MB_WINDOW_TOS_WL_MAIN=<Watchlist main-window title prefix>
MB_WINDOW_TOS_WL_EXPORT=<Watchlist export-dialog title prefix>
MB_WINDOW_TOS_WL_SYMBOLS=Symbols Import
```

Replace all placeholder values with the stable title prefixes used by the ThinkOrSwim windows on the current computer.

The values should normally be stable left-hand title prefixes rather than complete titles containing changing build numbers or Watchlist names.

For example:

```dotenv
MB_WINDOW_TOS_MAIN=Main@thinkorswim
```

can match a window whose complete title is similar to:

```text
Main@thinkorswim [build 1992]
```

### YAML layout

`MB_PWIDGET_YAML` must point to an existing pseudo-widget YAML file.

Example:

```dotenv
MB_PWIDGET_YAML=C:\Users\<username>\Documents\github\pwidget_layouts\layout_scanner3_v1p1dev2.yaml
```

The YAML root widget names are mapped to configuration values as follows:

| YAML root               | Configuration variable     |
| ----------------------- | -------------------------- |
| `win_main`              | `MB_WINDOW_TOS_MAIN`       |
| `win_logon`             | `MB_WINDOW_TOS_LOGON`      |
| `win_updater`           | `MB_WINDOW_TOS_UPDATE`     |
| `win_export`            | `MB_WINDOW_TOS_EXPORT`     |
| `win_wl_main`           | `MB_WINDOW_TOS_WL_MAIN`    |
| `win_wl_export`         | `MB_WINDOW_TOS_WL_EXPORT`  |
| `win_wl_symbols_import` | `MB_WINDOW_TOS_WL_SYMBOLS` |

## Running the survey

Run all commands from the repository root:

```cmd
cd C:\Users\<username>\Documents\github\ToS_gui_survey
```

### Interactive widget selection

```cmd
python widget_check.py
```

The program loads the YAML file and displays a Qt dialog containing the available widget names.

Select a widget and click **Continue**.

### Select a widget on the command line

```cmd
python widget_check.py btn_action_menu
```

Replace `btn_action_menu` with a widget name from the configured YAML layout.

The current workflow surveys one selected widget per run.

### Show configuration-loading details

```cmd
python widget_check.py --verbose
```

This prints the configuration sources and shows which values came from packaged defaults, Windows environment variables, or the project `.env` file.

### Use a different `.env` file

```cmd
python widget_check.py --env-file "C:\path\to\survey.env"
```

### Suppress the unannotated screenshot

By default, the program saves both a raw screenshot and an annotated screenshot.

To omit the raw screenshot:

```cmd
python widget_check.py btn_action_menu --no-raw-capture
```

### Display command-line help

```cmd
python widget_check.py --help
```

## Survey procedure

Before starting:

1. Start ThinkOrSwim.

2. Open the ThinkOrSwim window required by the selected pseudo-widget.

3. Place and size the ThinkOrSwim windows as expected by the YAML layout.

4. Run `widget_check.py`.

5. Select a widget from the dialog or provide its name on the command line.

6. Wait for the program to report:

   ```text
   Waiting for pose trigger (Ctrl+Shift+J)...
   ```

7. Press:

   ```text
   Ctrl+Shift+J
   ```

8. The program brings the corresponding ThinkOrSwim window forward.

9. A five-second delay allows time to prepare the interface.

10. The program captures and annotates the screen.

11. Close the OpenCV image window after reviewing the result.

## Output files

Capture output is written beneath:

```text
captures\
```

A typical run produces:

```text
captures\
├── pwidget-YYYY-MM-DD-HH-MM-SS-widget_name-raw.png
├── pwidget-YYYY-MM-DD-HH-MM-SS-widget_name-annotated.png
└── pwidget-YYYY-MM-DD-HH-MM-SS-widget_name-metadata.json
```

### Raw screenshot

The raw file is an unmodified full-screen capture.

It is omitted when `--no-raw-capture` is used.

### Annotated screenshot

The annotated file contains:

* bounding rectangles for the selected pseudo-widget;
* bounding rectangles for its ancestors;
* widget labels;
* center-point markers;
* a color legend showing pseudo-widget hierarchy depth.

### Metadata JSON

The metadata file records information such as:

* capture timestamp;
* selected widget name;
* full pseudo-widget path;
* YAML path and derived layout version;
* absolute coordinates;
* width and height;
* center coordinates;
* hierarchy level;
* raw and annotated image paths.

## Logging

Logs are written beneath:

```text
logs\
```

The daily log filename has this form:

```text
logs\scan_YYYY-MM-DD.log
```

Messages are written both to the log file and to the terminal.

The same daily file is appended to when the program is run more than once on the same day.

## Window matching

ThinkOrSwim window titles may contain changing information such as a build number or Watchlist name.

The configuration therefore uses title prefixes. The program searches for an open window whose title begins with the configured value.

When a matching root window is found, its current screen position is used to update the runtime pseudo-widget hierarchy before the capture.

The YAML width and height remain the reference dimensions. The program logs a warning when an open window differs from the YAML dimensions by more than the configured tolerance.

## Troubleshooting

### Missing configuration variable

Example:

```text
Missing required MB_* configuration variable(s):
 MB_WINDOW_TOS_WL_EXPORT
```

Add the missing variable to the project `.env` file or to the Windows environment.

Be careful about similarly named variables. The current `ToS_gui_survey` code requires:

```text
MB_WINDOW_TOS_WL_EXPORT
```

### YAML file not found

Confirm the value of:

```text
MB_PWIDGET_YAML
```

From CMD:

```cmd
echo %MB_PWIDGET_YAML%
```

When the value is supplied only by the project `.env`, use verbose mode instead:

```cmd
python widget_check.py --verbose
```

The resolved YAML path must point to an existing file.

### Invalid widget name

Run without a widget argument:

```cmd
python widget_check.py
```

The selection dialog will show the widget names currently available in the YAML layout.

The `mb-pwidget-tree` utility from `mb_tools` can also inspect the layout:

```cmd
mb-pwidget-tree "%MB_PWIDGET_YAML%"
```

### ThinkOrSwim window is not found

Confirm that:

* ThinkOrSwim is running;
* the required window or dialog is open;
* the configured title prefix matches the left side of the actual title;
* the correct YAML root is associated with the title variable;
* the window is not on a different Windows virtual desktop.

The `mb-window-survey` utility can help identify actual window titles:

```cmd
mb-window-survey
```

### Window size differs from YAML

Resize the ThinkOrSwim window to the expected dimensions or update the YAML layout after verifying the new geometry.

A size mismatch can make child pseudo-widget coordinates inaccurate.

### `Ctrl+Shift+J` is not detected

Make sure the terminal window remains open and that another application is not intercepting the shortcut.

If necessary, try running the terminal as Administrator, but normal execution should be attempted first.

### Screenshot appears incorrect

Check that:

* display scaling has not changed;
* monitor arrangement has not changed;
* ThinkOrSwim is on the expected monitor;
* the correct ThinkOrSwim window was brought forward;
* the YAML corresponds to the current ThinkOrSwim layout;
* no dialog moved during the five-second preparation delay.

## Project structure

```text
ToS_gui_survey\
├── widget_check.py       Main program
├── window_config.py      Required MB_* configuration
├── layout.py             YAML layout loading and flattening
├── window_utils.py       Wrappers around mb_tools.windowing
├── drawing.py            Screenshot annotation and metadata
├── monitoring.py         Window-position monitoring
├── input_handlers.py     Keyboard-trigger detection
├── dialog.py             Qt widget-selection dialog
├── logger.py             Terminal and file logging
├── scan_control.ui       Qt Designer UI resource
└── utils.py              Miscellaneous helpers
```

## Development notes

This repository currently relies on direct script execution and does not yet provide:

* Python package metadata;
* a dependency lock file;
* a `requirements.txt`;
* automated tests;
* an installed console entry point.

Possible future improvements include:

* adding a `pyproject.toml`;
* declaring runtime dependencies;
* adding a console command such as `tos-gui-survey`;
* adding configuration-validation tests;
* adding screenshot-path and metadata tests;
* separating reusable capture helpers from ThinkOrSwim-specific behavior.

## Safety and scope

This is a diagnostic and layout-validation tool.

It observes window positions, brings selected windows to the foreground, listens for a keyboard trigger, and captures screenshots. It does not submit trades or make account decisions.
