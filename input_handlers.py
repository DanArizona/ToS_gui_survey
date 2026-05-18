# input_handlers.py

import time
import keyboard


def is_ctrl_shift_j_pressed() -> bool:
    """Return True if Ctrl+Shift+J is currently pressed."""
    return keyboard.is_pressed('ctrl+shift+j')


def wait_for_pose_trigger(key_combo: str = 'ctrl+shift+i'):
    """
    Wait for a keyboard shortcut to be pressed.
    Default combo is Ctrl+Shift+I for triggering a pose.
    """
    print(f"Press {key_combo.upper()} when ready to take the screenshot...")
    while True:
        if keyboard.is_pressed(key_combo):
            print("Pose trigger received.")
            break
        time.sleep(0.1)
