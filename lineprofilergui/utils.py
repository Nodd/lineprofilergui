from functools import partial

from qtpy import QtCore, QtGui, QtWidgets

translate = partial(QtCore.QCoreApplication.translate, "self")


MONOSPACE_FONT = QtGui.QFont("Monospace")
MONOSPACE_FONT.setStyleHint(QtGui.QFont.Monospace)
MONOSPACE_FONT.setPointSize(9)

_ICON_IDS = {
    "OK": QtWidgets.QStyle.SP_DialogApplyButton,
    "NOK": QtWidgets.QStyle.SP_DialogCancelButton,  # Icon invalid field
    "START": QtWidgets.QStyle.SP_MediaPlay,  # actionRun
    "STOP": QtWidgets.QStyle.SP_MediaStop,  # actionAbort
    "ABORT": QtWidgets.QStyle.SP_BrowserStop,  # actionQuit
    "CONFIG": QtWidgets.QStyle.SP_FileDialogDetailedView,  # actionConfigure
    "SETTINGS": QtWidgets.QStyle.SP_FileDialogListView,  # actionSettings
    "BLANKFILE": QtWidgets.QStyle.SP_FileIcon,  # statsButton
    "READFILE": QtWidgets.QStyle.SP_FileDialogContentsView,  # scriptButton, kernprofButton
    "DIRECTORY": QtWidgets.QStyle.SP_DirIcon,  # wdirButton
    "EXPAND": QtWidgets.QStyle.SP_ToolBarVerticalExtensionButton,  # actionExpand_all
    "COLLAPSE": QtWidgets.QStyle.SP_ToolBarHorizontalExtensionButton,  # actionCollapse_all
    "QT": QtWidgets.QStyle.SP_TitleBarMenuButton,  # actionAbout_Qt
    "HELP": QtWidgets.QStyle.SP_DialogHelpButton,  # actionLine_profiler_documentation
    "INFO": QtWidgets.QStyle.SP_MessageBoxInformation,  # actionShowOutput, actionGithubLink
    "WARNING": QtWidgets.QStyle.SP_MessageBoxWarning,  # actionShowOutput
    "ERROR": QtWidgets.QStyle.SP_MessageBoxCritical,  # actionReportBug
    "RUNNING": QtWidgets.QStyle.SP_BrowserReload,  # statusbar_running_indicator, actionShowOutput
}

ICONS = {}
PIXMAPS = {}
PIXMAP_SIZE = 16


def icons_factory():
    for k, v in _ICON_IDS.items():
        icon = QtWidgets.QApplication.style().standardIcon(v)
        ICONS[k] = icon
        PIXMAPS[k] = icon.pixmap(PIXMAP_SIZE, PIXMAP_SIZE)
