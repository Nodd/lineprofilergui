import datetime
import os
import sys
from pathlib import Path
import textwrap
import urllib

import qtpy
from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Qt
import qtpy.compat as qtcompat

from .config import Config, Ui_ConfigDialog
from .tree import ResultsTreeWidget, load_profile_data
from .settings import UI_SettingsDialog
from .utils import translate as _, MONOSPACE_FONT, ICONS, PIXMAPS
from .process import KernprofRun
from . import __version__

LINE_PROFILER_GUI_GITHUB_URL = "https://github.com/Nodd/lineprofilergui"
LINE_PROFILER_DOC_URL = "https://github.com/pyutils/line_profiler#id2"


class UI_MainWindow(QtWidgets.QMainWindow):

    # Used for testing purposes
    profile_finished = QtCore.Signal()

    def __init__(self):
        self.config = Config()

        super().__init__()
        self.setup_ui()
        self.kernprof_run = KernprofRun(self.config)
        self.connect()

        self.profile_start_time = None

    def setup_ui(self):
        # Main window
        # app.setWindowIcon(QIcon(_WINDOW_ICON))
        self.resize(800, 600)

        # Results widget
        self.resultsTreeWidget = ResultsTreeWidget(self)
        self.resultsTreeWidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.resultsTreeWidget.setMinimumSize(300, 50)
        self.setCentralWidget(self.resultsTreeWidget)

        # Output widget
        self.dockOutputWidget = DockOutputWidget(self)
        self.dockOutputWidget.setObjectName("dockOutputWidget")
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dockOutputWidget)

        # Actions
        self.actionCollapse_all = QtWidgets.QAction(self)
        self.actionCollapse_all.setIcon(ICONS["COLLAPSE"])
        self.actionExpand_all = QtWidgets.QAction(self)
        self.actionExpand_all.setIcon(ICONS["EXPAND"])
        self.actionRun = QtWidgets.QAction(self)
        self.actionRun.setIcon(ICONS["START"])
        self.actionAbort = QtWidgets.QAction(self)
        self.actionAbort.setIcon(ICONS["STOP"])
        self.actionShowOutput = self.dockOutputWidget.toggleViewAction()
        self.actionShowOutput.setIcon(ICONS["INFO"])
        self.actionLoadLprof = QtWidgets.QAction(self)
        self.actionLoadLprof.setIcon(ICONS["READFILE"])
        self.actionQuit = QtWidgets.QAction(self)
        self.actionQuit.setIcon(ICONS["ABORT"])
        self.actionConfigure = QtWidgets.QAction(self)
        self.actionConfigure.setIcon(ICONS["CONFIG"])
        self.actionSettings = QtWidgets.QAction(self)
        self.actionSettings.setIcon(ICONS["SETTINGS"])
        self.actionLine_profiler_documentation = QtWidgets.QAction(self)
        self.actionLine_profiler_documentation.setIcon(ICONS["HELP"])
        self.actionGithubLink = QtWidgets.QAction(self)
        self.actionGithubLink.setIcon(ICONS["INFO"])
        self.actionReportBug = QtWidgets.QAction(self)
        self.actionReportBug.setIcon(ICONS["ERROR"])
        self.actionAbout_Qt = QtWidgets.QAction(self)
        self.actionAbout_Qt.setIcon(ICONS["QT"])

        # Menu bar
        self.menubar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menubar)

        # Profiling menu
        self.menuProfiling = QtWidgets.QMenu(self.menubar)
        self.menuProfiling.addAction(self.actionConfigure)
        self.menuProfiling.addSeparator()
        self.menuProfiling.addAction(self.actionRun)
        self.menuProfiling.addAction(self.actionAbort)
        self.menuProfiling.addAction(self.actionShowOutput)
        self.menuProfiling.addSeparator()
        self.menuProfiling.addAction(self.actionLoadLprof)
        self.menuProfiling.addSeparator()
        self.menuProfiling.addAction(self.actionQuit)
        self.menubar.addAction(self.menuProfiling.menuAction())

        # Display Menu
        self.menuDisplay = QtWidgets.QMenu(self.menubar)
        self.menuDisplay.addAction(self.actionCollapse_all)
        self.menuDisplay.addAction(self.actionExpand_all)
        self.menuDisplay.addSeparator()
        self.menuDisplay.addAction(self.actionSettings)
        self.menubar.addAction(self.menuDisplay.menuAction())

        # Help Menu
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.addAction(self.actionLine_profiler_documentation)
        self.menuHelp.addAction(self.actionGithubLink)
        self.menuHelp.addAction(self.actionReportBug)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout_Qt)
        self.menubar.addAction(self.menuHelp.menuAction())

        # Toolbar
        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.toolBar.addAction(self.actionConfigure)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionRun)
        self.toolBar.addAction(self.actionAbort)
        self.toolBar.addAction(self.actionShowOutput)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionCollapse_all)
        self.toolBar.addAction(self.actionExpand_all)
        self.toolBar.addSeparator()
        self.historyCombo = QtWidgets.QComboBox(self)
        self.historyCombo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.toolBar.addWidget(self.historyCombo)

        # Statusbar
        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar_running_indicator = QtWidgets.QLabel()
        self.statusbar_running_indicator.setPixmap(PIXMAPS["RUNNING"])
        self.statusbar_running_indicator.hide()
        self.statusbar_running_indicator_timer = QtCore.QTimer(self)
        self.statusbar_running_indicator_timer.timeout.connect(
            lambda: self.statusbar_running_indicator.setVisible(
                not self.statusbar_running_indicator.isVisible()
            )
        )
        self.statusbar.addPermanentWidget(self.statusbar_running_indicator)
        self.statusbar_time = QtWidgets.QLabel()
        self.statusbar.addWidget(self.statusbar_time)

        self.settingsDialog = UI_SettingsDialog(self)

        # Finalization
        self.retranslate_ui()
        self.read_settings()
        self.set_running_state(False)

    def connect(self):
        self.actionCollapse_all.triggered.connect(self.resultsTreeWidget.collapseAll)
        self.actionExpand_all.triggered.connect(self.resultsTreeWidget.expandAll)
        self.actionConfigure.triggered.connect(self.configure)
        self.actionSettings.triggered.connect(self.settingsDialog.show)
        self.actionRun.triggered.connect(self.profile)
        self.actionAbort.triggered.connect(self.kernprof_run.kill)
        self.actionShowOutput.toggled.connect(self.dockOutputWidget.setVisible)
        self.actionLoadLprof.triggered.connect(self.selectLprof)
        self.actionQuit.triggered.connect(QtWidgets.QApplication.instance().quit)
        self.actionLine_profiler_documentation.triggered.connect(
            lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(LINE_PROFILER_DOC_URL))
        )
        self.actionGithubLink.triggered.connect(
            lambda: QtGui.QDesktopServices.openUrl(
                QtCore.QUrl(LINE_PROFILER_GUI_GITHUB_URL)
            )
        )
        self.actionReportBug.triggered.connect(self.report_bug)
        self.actionAbout_Qt.triggered.connect(QtWidgets.QApplication.aboutQt)
        self.kernprof_run.output_text.connect(self.dockOutputWidget.append_log_text)
        self.kernprof_run.output_error.connect(self.dockOutputWidget.append_log_error)
        self.settingsDialog.accepted.connect(self.resultsTreeWidget.updateColonsVisible)
        self.historyCombo.currentIndexChanged.connect(self.load_history)

    def retranslate_ui(self):
        self.update_window_title()
        self.toolBar.setWindowTitle(_("Tool bar"))
        self.menuDisplay.setTitle(_("&Display"))
        self.menuProfiling.setTitle(_("&Profiling"))
        self.menuHelp.setTitle(_("&Help"))
        self.actionCollapse_all.setText(_("&Collapse all"))
        self.actionExpand_all.setText(_("&Expand all"))
        self.actionRun.setText(_("&Profile"))
        self.actionRun.setShortcut(_("F5"))
        self.actionAbort.setText(_("&Stop"))
        self.actionAbort.setShortcut(_("F6"))
        self.actionShowOutput.setText(_("&Console output"))
        self.actionShowOutput.setShortcut(_("F7"))
        self.actionLoadLprof.setText(_("&Load data..."))
        self.actionLoadLprof.setShortcut(_("Ctrl+O"))
        self.actionQuit.setText(_("&Quit"))
        self.actionQuit.setShortcut(_("Ctrl+Q"))
        self.actionConfigure.setText(_("&Configuration..."))
        self.actionConfigure.setShortcut(_("F4"))
        self.actionSettings.setText(_("&Settings..."))
        self.actionLine_profiler_documentation.setText(
            _("&Line-profiler documentation...")
        )
        self.actionLine_profiler_documentation.setShortcut(_("F1"))
        self.actionGithubLink.setText(_("&Github project..."))
        self.actionReportBug.setText(_("&Report bug..."))
        self.actionAbout_Qt.setText(_("&About Qt..."))

    def update_window_title(self):
        title = _("Line Profiler GUI")
        if self.config.script:
            title += f" - {self.config.script}"
        self.setWindowTitle(title)

    def closeEvent(self, event):
        self.write_settings()
        QtWidgets.QMainWindow.closeEvent(self, event)

    def write_settings(self):
        settings = QtCore.QSettings()
        settings.beginGroup("MainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("state", self.saveState())
        settings.endGroup()

    def read_settings(self):
        settings = QtCore.QSettings()
        settings.beginGroup("MainWindow")
        geometry = settings.value("geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
        state = settings.value("state")
        if state is not None:
            self.restoreState(state)
        settings.endGroup()

    @QtCore.Slot()
    def selectLprof(self):
        filename, _selfilter = qtcompat.getopenfilename(
            self,
            _("Select line profiler data"),
            "",
            _("Line profiler data") + " (*.lprof);; " + _("All files") + " (*.*)",
        )
        if filename:
            self.load_lprof(filename)

    @QtCore.Slot()
    def configure(self):
        Ui_ConfigDialog(self, self.config).exec()
        self.update_window_title()

    @QtCore.Slot()
    def profile(self):
        # Configuration dialog in case of invalid config
        if not self.config.isvalid:
            self.configure()
            if not self.config.isvalid:
                return

        # Start process
        Path(self.config.stats).unlink(missing_ok=True)
        self.dockOutputWidget.clear()
        process = self.kernprof_run.prepare()
        process.stateChanged.connect(self.set_running_state)
        process.finished.connect(self.process_finished)
        self.profile_start_time = datetime.datetime.now()
        self.kernprof_run.start()

    @QtCore.Slot(QtCore.QProcess.ProcessState)
    def set_running_state(self, running):
        self.actionRun.setEnabled(not running)
        self.actionAbort.setEnabled(running)
        self.actionConfigure.setEnabled(not running)
        self.statusbar_running_indicator.setVisible(running)
        self.dockOutputWidget.set_running_state(running)
        if running:
            self.setCursor(Qt.WaitCursor)
            self.statusbar_running_indicator_timer.start(800)
        else:
            self.unsetCursor()
            self.statusbar_running_indicator_timer.stop()
            # status icons are set in self.process_finished()

    @QtCore.Slot(int, QtCore.QProcess.ExitStatus)
    def process_finished(self, exit_code, exit_status):
        """Note: if process was aborted, exit_status should be 1"""
        # Time and duration values
        profile_stop_time = datetime.datetime.now()
        profile_duration = profile_stop_time - self.profile_start_time
        profile_time_str = profile_stop_time.strftime("%X")
        profile_duration_str = str(profile_duration).lstrip("0:")
        if profile_duration_str.startswith("."):
            profile_duration_str = "0" + profile_duration_str

        # Statusbar text
        if exit_status:
            text = _(
                "Last profiling was terminated at {time} after running for {duration}s"
            ).format(time=profile_time_str, duration=profile_duration_str,)
        elif exit_code:
            text = _(
                "Last profiling terminated with exit code {code} at {time} after running for {duration}s"
            ).format(
                code=exit_code, time=profile_time_str, duration=profile_duration_str
            )
        else:
            text = _("Last profiling ended at {time} and ran for {duration}s").format(
                time=profile_time_str, duration=profile_duration_str
            )
        self.statusbar_time.setText(text)

        # Output console status
        self.dockOutputWidget.set_exit_state(exit_status or exit_code)

        # Load .lprof file
        title = _("{duration}s at {time}").format(
            duration=profile_duration_str, time=profile_time_str
        )
        try:
            self.load_lprof(self.config.stats, title)
        except FileNotFoundError:
            if self.config.stats_tmp:
                self.resultsTreeWidget.warning_message(_("No profiling results"))
            else:
                self.resultsTreeWidget.warning_message(
                    _('Profiling results not found: "{file}"').format(
                        file=self.config.stats
                    )
                )

        # For testing purposes
        self.profile_finished.emit()

    def load_lprof(self, lprof_file, title=None):
        profile_data = load_profile_data(lprof_file)
        if not title:
            time = datetime.datetime.now().strftime("%X")
            name = os.path.basename(lprof_file)
            title = _("{name} at {time}").format(name=name, time=time)
        self.historyCombo.insertItem(0, title, profile_data)
        self.historyCombo.setCurrentIndex(0)

    @QtCore.Slot(int)
    def load_history(self, index):
        if index < 0:
            return
        self.resultsTreeWidget.show_tree(self.historyCombo.currentData())

    @QtCore.Slot()
    def report_bug(self):
        from line_profiler import __version__ as line_profiler_version

        body = textwrap.dedent(
            f"""
            # Description of the problem
            <!-- Explain your problem in detail -->





            # Environment and versions
            * **Line Profiler GUI**: *{__version__}*
            * **python**: *{sys.version}*
            * **OS**: *{sys.platform}*
            * **line_profiler**: *{line_profiler_version}*
            * **QtPy API**: *{qtpy.API} {qtpy.PYQT_VERSION if qtpy.API.startswith("pyqt") else qtpy.PYSIDE_VERSION}*
            * **Qt**: *{qtpy.QT_VERSION}*
            """
        ).strip()
        url = f"{LINE_PROFILER_GUI_GITHUB_URL}/issues/new?body={urllib.parse.quote_plus(body)}"
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))


class DockOutputWidget(QtWidgets.QDockWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # Console ouput widget
        self.outputWidget = QtWidgets.QPlainTextEdit()
        self.outputWidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.outputWidget.setReadOnly(True)
        self.outputWidget.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByKeyboard
            | QtCore.Qt.LinksAccessibleByMouse
            | QtCore.Qt.TextBrowserInteraction
            | QtCore.Qt.TextSelectableByKeyboard
            | QtCore.Qt.TextSelectableByMouse
        )
        self.outputWidget.setFont(MONOSPACE_FONT)
        self.outputWidget.setMinimumSize(300, 50)
        self.setWidget(self.outputWidget)

    def set_running_state(self, running):
        actionShowOutput = self.toggleViewAction()
        actionShowOutput.setIcon(ICONS["RUNNING" if running else "INFO"])
        if running:
            self.setWindowTitle(_("{} Console output").format("🔄"))
            # self.setWindowTitle() overrides the action text
            # We reset it without the icon to avoid a ugly menu entry
            actionShowOutput.setText(_("&Console output"))
        else:
            self.setWindowTitle(_("Console output"))

    def set_exit_state(self, error):
        actionShowOutput = self.toggleViewAction()
        if error:
            self.show()
            self.activateWindow()
            self.outputWidget.setFocus(Qt.OtherFocusReason)
            actionShowOutput.setIcon(ICONS["WARNING"])
            self.setWindowTitle(_("{} Console output").format("⚠"))
        else:
            actionShowOutput.setIcon(ICONS["INFO"])
            self.setWindowTitle(_("{} Console output").format("ⓘ"))
        # self.setWindowTitle() overrides the action text
        # We reset it without the icon to avoid a ugly menu entry
        actionShowOutput.setText(_("&Console output"))

    @QtCore.Slot(str)
    def append_log_text(self, text):
        self.outputWidget.appendPlainText(text)

    @QtCore.Slot(str)
    def append_log_error(self, text):
        self.outputWidget.appendHtml(f'<p style="color:red;white-space:pre">{text}</p>')

    def clear(self):
        self.outputWidget.clear()
