# ToS GUI Survey

`ToS_gui_survey` is a Windows diagnostic utility for inspecting and validating the pseudo-widget layouts used by the MasterBot ThinkOrSwim GUI automation projects.

The program loads a pseudo-widget hierarchy from YAML, associates its root widgets with live ThinkOrSwim windows, refreshes those roots from the current desktop geometry, lets the operator select a pseudo-widget, and captures an annotated screenshot showing the selected widget and its ancestors.

The project is intended primarily to support development and maintenance of:

- `pwidget_layouts`;
- `ToS_scanner`;
- the reusable window/pseudo-widget functionality in `mb_tools`.

It is a diagnostic tool. It does not place trades or make brokerage-account decisions.

---

## Platform

The current implementation targets:

- Windows 11;
- Python 3.12;
- ThinkOrSwim desktop;
- a compatible pseudo-widget YAML layout;
- the `mb_tools` Python package.

The program relies on Windows-specific window-management and keyboard APIs and is not expected to run unchanged on Linux or macOS.

---

## Repository entry point

Run the project from the repository root:

```cmd
python widget_check.py
```

The repository is currently script-based and does not install a separate console command.

---

## Installation

### 1. Clone the related repositories

A typical development layout is:

```text
C:\Users\<username>\Documents\github\
├── mb_tools
├── pwidget_layouts
└── ToS_gui_survey
```

`ToS_scanner` is also normally present elsewhere in the same development environment.

### 2. Activate a Python environment

Example:

```cmd
conda activate sea-green
```

Python 3.12 is recommended.

### 3. Install `mb_tools`

For development, install the local `mb_tools` repository in editable mode with its Qt support:

```cmd
python -m pip install -e "C:\Users\<username>\Documents\github\mb_tools[qt]"
```

### 4. Install the remaining runtime dependencies

`ToS_gui_survey` does not currently have its own `pyproject.toml` or `requirements.txt`.

Install the remaining dependencies with:

```cmd
python -m pip install keyboard opencv-python numpy pyautogui pywin32
```

Verify the important imports:

```cmd
python -c "import cv2, keyboard, numpy, pyautogui, win32api; import mb_tools; print('Imports OK')"
```

---

## Configuration

The program loads `MB_*` configuration through:

```python
mb_tools.config.load_mb_config()
```

Configuration follows the standard `mb_tools` precedence:

```text
project .env
    >
Windows MB_* environment variables
    >
mb_tools defaults.env
```

A value in the project's `.env` therefore overrides the corresponding Windows environment value. Packaged defaults are used only when neither higher-precedence source defines the setting.

By default, the project-specific environment file is:

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

Replace the placeholder values with stable title prefixes appropriate for the current ThinkOrSwim installation.

The program generally expects stable left-hand title prefixes rather than complete window titles containing changing build numbers, Watchlist names, or other dynamic text.

For example:

```dotenv
MB_WINDOW_TOS_MAIN=Main@thinkorswim
```

can match a complete title such as:

```text
Main@thinkorswim [build 1992]
```

### Important Watchlist export variable

`ToS_gui_survey` currently uses:

```text
MB_WINDOW_TOS_WL_EXPORT
```

Do not substitute similarly named variables from other MasterBot projects unless the program itself is changed to use them.

### YAML layout

`MB_PWIDGET_YAML` must point to an existing pseudo-widget YAML file.

Example:

```dotenv
MB_PWIDGET_YAML=C:\Users\<username>\Documents\github\pwidget_layouts\layout_scanner3_v1p1dev2.yaml
```

The current YAML root widgets map to configuration variables as follows:

| YAML root | Configuration variable |
| --- | --- |
| `win_main` | `MB_WINDOW_TOS_MAIN` |
| `win_logon` | `MB_WINDOW_TOS_LOGON` |
| `win_updater` | `MB_WINDOW_TOS_UPDATE` |
| `win_export` | `MB_WINDOW_TOS_EXPORT` |
| `win_wl_main` | `MB_WINDOW_TOS_WL_MAIN` |
| `win_wl_export` | `MB_WINDOW_TOS_WL_EXPORT` |
| `win_wl_symbols_import` | `MB_WINDOW_TOS_WL_SYMBOLS` |

---

## Running the survey

Run commands from the repository root:

```cmd
cd C:\Users\<username>\Documents\github\ToS_gui_survey
```

### Interactive widget selection

```cmd
python widget_check.py
```

The program loads the YAML layout and opens a Qt dialog containing the available pseudo-widget names.

Choose a widget and click **Continue**.

### Select a widget on the command line

```cmd
python widget_check.py btn_action_menu
```

Replace `btn_action_menu` with a widget name from the active YAML layout.

The current workflow surveys one selected widget per run.

### Show configuration-loading details

```cmd
python widget_check.py --verbose
```

Verbose mode shows the resolved configuration and where values came from, including:

- packaged defaults;
- Windows environment variables;
- the project `.env` file.

### Use a different `.env` file

```cmd
python widget_check.py --env-file "C:\path\to\survey.env"
```

### Suppress the raw screenshot

By default, both raw and annotated screenshots are saved.

To omit the raw screenshot:

```cmd
python widget_check.py btn_action_menu --no-raw-capture
```

### Display command-line help

```cmd
python widget_check.py --help
```

---

## Survey procedure

Before starting:

1. Start ThinkOrSwim.
2. Open the ThinkOrSwim window or dialog containing the pseudo-widget you want to inspect.
3. Position and size the relevant ThinkOrSwim windows as expected by the active YAML layout.
4. Run `widget_check.py`.
5. Select the pseudo-widget interactively or supply its name on the command line.
6. Wait for:

   ```text
   Waiting for pose trigger (Ctrl+Shift+J)...
   ```

7. Press:

   ```text
   Ctrl+Shift+J
   ```

8. The program brings the corresponding ThinkOrSwim root window to the foreground.
9. A five-second preparation delay gives the operator time to arrange any required menus or dialogs.
10. The screen is captured.
11. The selected pseudo-widget and its ancestor hierarchy are drawn on the captured image.
12. Review the OpenCV display and close it when finished.

The preparation delay is especially useful when a pseudo-widget exists only after a menu or dialog is opened.

---

## Output files

Capture output is written below:

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

The raw screenshot is an unmodified full-screen capture.

It is omitted when:

```text
--no-raw-capture
```

is used.

### Annotated screenshot

The annotated screenshot includes visual information such as:

- the selected pseudo-widget boundary;
- ancestor pseudo-widget boundaries;
- widget labels;
- center-point markers;
- hierarchy-depth annotation.

The purpose is to make it easy to compare the YAML geometry with the actual ThinkOrSwim interface.

### Metadata JSON

The metadata file records diagnostic information such as:

- capture timestamp;
- selected widget name;
- full pseudo-widget path;
- YAML path;
- derived layout version;
- absolute coordinates;
- width and height;
- center coordinates;
- hierarchy level;
- raw and annotated output paths.

---

## Logging

Logs are written below:

```text
logs\
```

The current daily filename format is:

```text
logs\scan_YYYY-MM-DD.log
```

Messages are written both to the terminal and to the daily log.

Multiple runs on the same day append to the same file.

---

## Window matching

ThinkOrSwim window titles may include changing information such as build numbers or Watchlist names.

The configuration therefore normally uses title prefixes.

The program searches the Windows desktop for an open window whose title begins with the configured value.

When a matching root window is found, its current screen location is used to refresh the runtime pseudo-widget hierarchy before the screenshot is taken.

The YAML width and height remain the reference geometry.

If the live window dimensions differ materially from the YAML reference dimensions, the program logs a warning because descendant pseudo-widget coordinates may no longer be reliable.

---

## Relationship to `pwidget_layouts`

The `pwidget_layouts` repository stores the versioned YAML pseudo-widget definitions used by this program and by `ToS_scanner`.

A typical workflow is:

```text
ThinkOrSwim GUI
      |
      v
ToS_gui_survey
      |
      v
inspect / validate geometry
      |
      v
pwidget_layouts YAML
      |
      v
ToS_scanner
```

`ToS_gui_survey` is therefore primarily a measurement and validation tool.

The YAML layout itself remains separate from the survey program.

---

## Related projects

### `pwidget_layouts`

Stores the versioned YAML pseudo-widget layouts surveyed and validated by this project.

`MB_PWIDGET_YAML` normally points to a file in that repository.

### `mb_tools`

Provides reusable infrastructure used by this project, including:

- configuration loading;
- pseudo-widget support;
- window discovery and manipulation;
- shared diagnostic utilities.

Useful installed commands include:

```text
mb-window-survey
mb-pwidget-tree
```

### `ToS_scanner`

Consumes validated pseudo-widget layouts for live ThinkOrSwim automation, including:

- scanner export;
- Watchlist export;
- Watchlist ADD;
- Watchlist REPLACE;
- interaction with ThinkOrSwim dialogs.

The survey project is intended to reduce the risk of modifying those live automation coordinates blindly.

---

## Troubleshooting

### Missing configuration variable

Example:

```text
Missing required MB_* configuration variable(s):
 MB_WINDOW_TOS_WL_EXPORT
```

Add the missing setting to either:

- the project `.env`; or
- the Windows environment.

Remember that the current survey program specifically requires:

```text
MB_WINDOW_TOS_WL_EXPORT
```

### YAML file not found

Check:

```cmd
echo %MB_PWIDGET_YAML%
```

If the setting exists only in the project `.env`, use:

```cmd
python widget_check.py --verbose
```

to see the resolved value.

The final path must point to an existing YAML file.

### Invalid widget name

Run without a widget argument:

```cmd
python widget_check.py
```

The selection dialog shows the pseudo-widgets currently available in the active YAML layout.

You can also inspect the hierarchy with:

```cmd
mb-pwidget-tree "%MB_PWIDGET_YAML%"
```

### ThinkOrSwim window is not found

Confirm that:

- ThinkOrSwim is running;
- the required window or dialog is open;
- the configured title prefix matches the beginning of the real title;
- the correct YAML root maps to the correct configuration variable;
- the window is on the current Windows virtual desktop.

The `mb-window-survey` utility can help identify the actual window titles:

```cmd
mb-window-survey
```

### Window size differs from YAML

Resize the ThinkOrSwim window to the expected dimensions or update the YAML only after validating the new geometry.

A size mismatch can make child pseudo-widget coordinates inaccurate.

### `Ctrl+Shift+J` is not detected

Make sure:

- the terminal remains open;
- another application is not intercepting the shortcut.

Normal execution should be attempted first. Running the terminal as Administrator should be treated as a troubleshooting step rather than the default.

### Screenshot appears incorrect

Check that:

- Windows display scaling has not changed;
- monitor arrangement has not changed;
- ThinkOrSwim is on the expected monitor;
- the correct ThinkOrSwim window was brought forward;
- the YAML matches the current ThinkOrSwim layout;
- no dialog moved during the five-second preparation delay.

### `qmlls` usage popup appears when opening the project in VS Code

A popup titled:

```text
qmlls
```

that displays QML Language Server command-line usage is editor tooling. It is not an error from `ToS_gui_survey`.

`qmlls` is the Qt/QML Language Server included with PySide6. This project is a Python/PySide6 application and does not currently use QML, so the QML language server is not required.

If the **Qt for Python** VS Code extension launches `qmlls` incorrectly, disable it for this workspace.

In VS Code:

1. Open **Settings**.
2. Select the **Workspace** settings scope.
3. Search for `qmlls`.
4. Disable **Qt for Python: Qmlls Enabled**.

The equivalent workspace setting is:

```json
{
    "qtForPython.qmlls.enabled": false
}
```

Disabling this setting does not prevent the project from using PySide6 or Qt Designer `.ui` files.

---

## Project structure

Important current files include:

```text
ToS_gui_survey\
├── widget_check.py       Main survey program
├── window_config.py      Required MB_* configuration
├── layout.py             YAML loading and pseudo-widget flattening
├── window_utils.py       Wrappers around mb_tools window utilities
├── drawing.py            Screenshot annotation and metadata
├── monitoring.py         Window-position monitoring
├── input_handlers.py     Keyboard trigger handling
├── dialog.py             Qt widget-selection dialog
├── logger.py             Terminal and file logging
├── scan_control.ui       Qt Designer UI resource
└── utils.py              Miscellaneous helpers
```

Generated output typically appears under:

```text
captures\
logs\
```

---

## Suggested pseudo-widget development workflow

When changing a ThinkOrSwim layout:

1. Start from a known working YAML layout.
2. Copy it to a new development-version filename.
3. Change only the pseudo-widget definitions that need adjustment.
4. Select the affected widget with `ToS_gui_survey`.
5. Capture and inspect its annotated geometry.
6. Inspect the hierarchy with `mb-pwidget-tree`.
7. Test the corresponding `ToS_scanner` action.
8. Commit the YAML and any useful tree report to `pwidget_layouts`.
9. Promote the layout to a stable version only after the affected GUI workflows are validated.

For critical GUI actions, state verification should be preferred over assuming that a visually plausible automated click succeeded.

---

## GUI limitations

Pseudo-widget automation depends on a visible, correctly arranged desktop.

Failures can occur when:

- a required window is closed;
- a dialog appears in an unexpected location;
- another application obscures the intended control;
- Windows display scaling changes;
- monitor arrangement changes;
- ThinkOrSwim changes its interface;
- the active YAML no longer matches the live application.

A known example from the broader MasterBot project is a window obscuring part of the ThinkOrSwim `Symbols Import` dialog. In that case, an automated click can land on the wrong window even though the automation sequence appears to continue.

The survey utility helps diagnose geometry, but downstream applications should still verify critical resulting state.

---

## Development notes

This repository currently uses direct script execution and does not yet provide:

- Python package metadata;
- a dependency lock file;
- a `requirements.txt`;
- an automated test suite;
- an installed console entry point.

Possible future improvements include:

- adding a `pyproject.toml`;
- declaring runtime dependencies explicitly;
- adding a console command such as `tos-gui-survey`;
- adding configuration-validation tests;
- adding metadata/output-path tests;
- separating reusable capture helpers from ThinkOrSwim-specific behavior.

These improvements are useful but are not required for the current layout-survey workflow.

---

## Repository scope

This repository should contain:

- the survey/diagnostic source code;
- Qt UI resources used by the survey tool;
- project documentation.

Versioned pseudo-widget YAML definitions should normally remain in:

```text
pwidget_layouts
```

rather than being duplicated here.

---

## Safety and scope

`ToS_gui_survey` is a diagnostic and layout-validation tool.

It can:

- inspect window positions;
- bring a selected window to the foreground;
- listen for a keyboard trigger;
- capture screenshots;
- annotate pseudo-widget geometry;
- write diagnostic metadata.

It does not:

- place trades;
- submit brokerage orders;
- modify account positions;
- make investment decisions.

---

## Security

Do not commit:

- brokerage credentials;
- passwords;
- API secrets;
- token files;
- private account information;
- project `.env` files containing sensitive configuration.

Captured screenshots should also be reviewed before they are committed or shared, because they may contain visible application or account information.

---

## Development status

`ToS_gui_survey` is actively used to support the current ThinkOrSwim automation proof of concept.

Its primary role is to help keep pseudo-widget geometry understandable, inspectable, and independently testable as the ThinkOrSwim layout and downstream scanner automation evolve.
