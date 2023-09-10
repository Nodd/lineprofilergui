import os

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Qt


def apply_dark_theme():
    # taken from https://stackoverflow.com/questions/15035767/is-the-qt-5-dark-fusion-theme-available-for-windows

    QtWidgets.QApplication.setStyle("Fusion")

    # Now use a palette to switch to dark colors: 2A82DA
    gray25 = QtGui.QColor(25, 25, 25)
    gray35 = QtGui.QColor(35, 35, 35)
    gray53 = QtGui.QColor(53, 53, 53)
    grayblue = QtGui.QColor(42, 130, 218)
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, gray53)
    dark_palette.setColor(QtGui.QPalette.WindowText, Qt.white)
    dark_palette.setColor(QtGui.QPalette.Base, gray35)
    dark_palette.setColor(QtGui.QPalette.AlternateBase, gray53)
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, gray25)
    dark_palette.setColor(QtGui.QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QtGui.QPalette.Text, Qt.white)
    dark_palette.setColor(QtGui.QPalette.Button, gray53)
    dark_palette.setColor(QtGui.QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QtGui.QPalette.BrightText, Qt.red)
    dark_palette.setColor(QtGui.QPalette.Link, grayblue)
    dark_palette.setColor(QtGui.QPalette.Highlight, grayblue)
    dark_palette.setColor(QtGui.QPalette.HighlightedText, gray35)
    dark_palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.Button, gray53)
    dark_palette.setColor(
        QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, Qt.darkGray
    )
    dark_palette.setColor(
        QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, Qt.darkGray
    )
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, Qt.darkGray)
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Light, gray53)
    QtWidgets.QApplication.setPalette(dark_palette)


def apply_default_theme():
    styles = QtWidgets.QStyleFactory.keys()
    style = "WindowsVista" if "WindowsVista" in styles else "Fusion"
    QtWidgets.QApplication.setPalette(QtWidgets.QApplication.style().standardPalette())
    QtWidgets.QApplication.setStyle(style)


def is_windows_dark_theme():
    """Detect Windows theme."""
    # From https://successfulsoftware.net/2021/03/31/how-to-add-a-dark-theme-to-your-qt-application/
    settings = QtCore.QSettings(
        "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
        QtCore.QSettings.NativeFormat,
    )
    return settings.value("AppsUseLightTheme", 1) == 0


def update_theme():
    settings = QtCore.QSettings()
    theme = settings.value("theme", "os", str)

    if theme not in ("light", "dark"):
        if os.name == "nt":
            theme = "dark" if is_windows_dark_theme() else "light"
        else:
            # TODO: Check on mac and linux ?
            theme = "light"

    if theme == "light":
        apply_default_theme()
    elif theme == "dark":
        apply_dark_theme()
