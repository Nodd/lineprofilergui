from functools import partial

from qtpy import QtCore, QtGui, QtWidgets

translate = partial(QtCore.QCoreApplication.translate, "self")


MONOSPACE_FONT = QtGui.QFont("Monospace")
MONOSPACE_FONT.setStyleHint(QtGui.QFont.Monospace)
MONOSPACE_FONT.setPointSize(9)

_ICON_IDS = {
    "OK": QtWidgets.QStyle.SP_DialogApplyButton,
    "NOK": QtWidgets.QStyle.SP_DialogCancelButton,
    "START": QtWidgets.QStyle.SP_MediaPlay,
    "STOP": QtWidgets.QStyle.SP_MediaStop,
    "ABORT": QtWidgets.QStyle.SP_BrowserStop,
    "CONFIG": QtWidgets.QStyle.SP_FileDialogDetailedView,
    "FILE": QtWidgets.QStyle.SP_FileIcon,
    "DIRECTORY": QtWidgets.QStyle.SP_DirIcon,
    "EXPAND": QtWidgets.QStyle.SP_ToolBarVerticalExtensionButton,
    "COLLAPSE": QtWidgets.QStyle.SP_ToolBarHorizontalExtensionButton,
    "QT": QtWidgets.QStyle.SP_TitleBarMenuButton,
    "HELP": QtWidgets.QStyle.SP_MessageBoxQuestion,
    "INFO": QtWidgets.QStyle.SP_MessageBoxInformation,
}

ICONS = {}
PIXMAPS = {}
PIXMAP_SIZE = 16


def _icons_factory():
    for k, v in _ICON_IDS.items():
        icon = QtWidgets.QApplication.style().standardIcon(v)
        ICONS[k] = icon
        PIXMAPS[k] = icon.pixmap(PIXMAP_SIZE, PIXMAP_SIZE)
