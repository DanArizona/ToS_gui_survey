# dialog.py

from typing import Optional, List
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton
)


def run_widget_selection_dialog(widget_names: List[str]) -> Optional[str]:
    """Show a simple dialog listing widget names; return the selected name or None if canceled."""

    app = QApplication.instance() or QApplication([])

    dialog = QDialog()
    dialog.setWindowTitle("Select a Widget")

    layout = QVBoxLayout(dialog)

    list_widget = QListWidget()
    list_widget.addItems(sorted(widget_names))
    layout.addWidget(list_widget)

    continue_button = QPushButton("Continue")
    continue_button.setEnabled(False)
    layout.addWidget(continue_button)

    selected_name = None

    def on_selection_changed():
        nonlocal selected_name
        selected_items = list_widget.selectedItems()
        if selected_items:
            selected_name = selected_items[0].text()
            continue_button.setEnabled(True)
        else:
            selected_name = None
            continue_button.setEnabled(False)

    list_widget.itemSelectionChanged.connect(on_selection_changed)
    continue_button.clicked.connect(dialog.accept)

    dialog.exec()
    return selected_name


class WidgetSelectionDialog(QDialog):
    """More robust dialog with internal state for widget selection."""
    def __init__(self, widget_names: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Widget")
        self.selected_widget = None

        layout = QVBoxLayout()

        self.label = QLabel("Select a widget from the list below:")
        layout.addWidget(self.label)

        self.list_widget = QListWidget()
        self.list_widget.addItems(sorted(widget_names))
        layout.addWidget(self.list_widget)

        self.continue_button = QPushButton("Continue")
        self.continue_button.setEnabled(False)
        layout.addWidget(self.continue_button)

        self.setLayout(layout)
        self.setMinimumWidth(300)

        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.continue_button.clicked.connect(self.accept)

    def on_selection_changed(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            self.selected_widget = selected_items[0].text()
            self.continue_button.setEnabled(True)
        else:
            self.selected_widget = None
            self.continue_button.setEnabled(False)
