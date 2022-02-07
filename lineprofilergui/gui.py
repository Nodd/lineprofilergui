import datetime
import os

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Qt
import qtpy.compat as qtcompat

from .config import Config, Ui_ConfigDialog
from .tree import ResultsTreeWidget, load_profile_data
from .settings import UI_SettingsDialog
from .utils import translate as _, MONOSPACE_FONT, _icons_factory, ICONS, PIXMAPS
from .process import KernprofRun

LINE_PROFILER_DOC_URL = "https://github.com/pyutils/line_profiler#id2"


class UI_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        self.config = Config()

        QtWidgets.QMainWindow.__init__(self)
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
        self.dockOutputWidget = QtWidgets.QDockWidget(self)
        self.dockOutputWidget.setWidget(self.outputWidget)
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
        self.actionQuit = QtWidgets.QAction(self)
        self.actionQuit.setIcon(ICONS["ABORT"])
        self.actionConfigure = QtWidgets.QAction(self)
        self.actionConfigure.setIcon(ICONS["CONFIG"])
        self.actionSettings = QtWidgets.QAction(self)
        self.actionSettings.setIcon(ICONS["SETTINGS"])
        self.actionLine_profiler_documentation = QtWidgets.QAction(self)
        self.actionLine_profiler_documentation.setIcon(ICONS["HELP"])
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
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout_Qt)
        self.menubar.addAction(self.menuHelp.menuAction())

        # Toolbar
        self.toolBar = QtWidgets.QToolBar(self)
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
        self.set_running_state(False)

    def connect(self):
        self.actionCollapse_all.triggered.connect(self.resultsTreeWidget.collapseAll)
        self.actionExpand_all.triggered.connect(self.resultsTreeWidget.expandAll)
        self.actionConfigure.triggered.connect(self.configure)
        self.actionSettings.triggered.connect(self.settingsDialog.show)
        self.actionRun.triggered.connect(self.profile)
        self.actionAbort.triggered.connect(self.kernprof_run.kill)
        self.actionShowOutput.toggled.connect(self.outputWidget.setVisible)
        self.actionQuit.triggered.connect(QtWidgets.QApplication.instance().quit)
        self.actionLine_profiler_documentation.triggered.connect(
            lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(LINE_PROFILER_DOC_URL))
        )
        self.actionAbout_Qt.triggered.connect(QtWidgets.QApplication.aboutQt)
        self.kernprof_run.output_text.connect(self.append_log_text)
        self.kernprof_run.output_error.connect(self.append_log_error)
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
        self.actionQuit.setText(_("&Quit"))
        self.actionQuit.setShortcut(_("Ctrl+Q"))
        self.actionConfigure.setText(_("&Configuration..."))
        self.actionConfigure.setShortcut(_("Ctrl+O"))
        self.actionSettings.setText(_("&Settings..."))
        self.actionLine_profiler_documentation.setText(
            _("&Line-profiler documentation...")
        )
        self.actionLine_profiler_documentation.setShortcut(_("F1"))
        self.actionAbout_Qt.setText(_("&About Qt..."))

    def update_window_title(self):
        title = _("Line Profiler GUI")
        if self.config.script:
            title += f" - {self.config.script}"
        self.setWindowTitle(title)

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
        self.outputWidget.clear()
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
        if running:
            self.setCursor(Qt.WaitCursor)
            self.statusbar_running_indicator_timer.start(800)
            self.actionShowOutput.setIcon(ICONS["RUNNING"])
            self.dockOutputWidget.setWindowTitle(_("{} Console output").format("🔄"))
            # self.dockOutputWidget.setWindowTitle() overrides the action text
            # We reset it without the icon to avoid a ugly menu entry
            self.actionShowOutput.setText(_("&Console output"))
        else:
            self.unsetCursor()
            self.statusbar_running_indicator_timer.stop()
            # status icons are set in self.process_finished()

    @QtCore.Slot(int, QtCore.QProcess.ExitStatus)
    def process_finished(self, exit_code, exit_status):
        profile_stop_time = datetime.datetime.now()
        profile_duration = profile_stop_time - self.profile_start_time
        profile_time_str = profile_stop_time.strftime("%X")
        profile_duration_str = str(profile_duration).lstrip("0:")
        self.statusbar_time.setText(
            _("Last profiling ended at {time} and ran for {duration}s").format(
                time=profile_time_str, duration=profile_duration_str,
            )
        )
        if exit_code or exit_status:
            self.dockOutputWidget.show()
            self.dockOutputWidget.activateWindow()
            self.outputWidget.setFocus(Qt.OtherFocusReason)
            self.actionShowOutput.setIcon(ICONS["WARNING"])
            self.dockOutputWidget.setWindowTitle(_("{} Console output").format("⚠"))
        else:
            self.actionShowOutput.setIcon(ICONS["INFO"])
            self.dockOutputWidget.setWindowTitle(_("{} Console output").format("ⓘ"))
        # self.dockOutputWidget.setWindowTitle() overrides the action text
        # We reset it without the icon to avoid a ugly menu entry
        self.actionShowOutput.setText(_("&Console output"))

        title = f"{profile_duration_str}s at {profile_time_str}"
        self.load_lprof(self.config.stats, title)

    def load_lprof(self, lprof_file, title=None):
        profile_data = load_profile_data(lprof_file)
        if not title:
            title = os.path.basename(lprof_file)
        self.historyCombo.insertItem(0, title, profile_data)
        self.historyCombo.setCurrentIndex(0)

    @QtCore.Slot(str)
    def append_log_text(self, text):
        self.outputWidget.appendPlainText(text)

    @QtCore.Slot(str)
    def append_log_error(self, text):
        self.outputWidget.appendHtml(f'<p style="color:red;white-space:pre">{text}</p>')

    @QtCore.Slot(int)
    def load_history(self, index):
        if index < 0:
            return
        self.resultsTreeWidget.show_tree(self.historyCombo.currentData())
