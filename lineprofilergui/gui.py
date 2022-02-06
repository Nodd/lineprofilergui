from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Qt
import qtpy.compat as qtcompat

from .config import Config, Ui_ConfigDialog
from .tree import ResultsTreeWidget
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

    def setup_ui(self):
        # Main window
        self.setObjectName("UI_MainWindow")
        # app.setWindowIcon(QIcon(_WINDOW_ICON))
        self.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.centralLayout.setContentsMargins(0, 6, 0, 0)
        self.centralLayout.setObjectName("centralLayout")
        self.setCentralWidget(self.centralwidget)

        # Results tab
        self.resultsTab = QtWidgets.QWidget()
        self.resultsTab.setObjectName("resultsTab")
        self.resultsTabLayout = QtWidgets.QVBoxLayout(self.resultsTab)
        self.resultsTabLayout.setContentsMargins(0, 0, 0, 0)
        self.resultsTabLayout.setObjectName("resultsTabLayout")
        self.resultsTreeWidget = ResultsTreeWidget(self.resultsTab)
        self.resultsTreeWidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.resultsTreeWidget.setObjectName("resultsTreeWidget")
        self.resultsTabLayout.addWidget(self.resultsTreeWidget)

        # Output tab
        self.outputTab = QtWidgets.QWidget()
        self.outputTab.setObjectName("outputTab")
        self.outputTabLayout = QtWidgets.QVBoxLayout(self.outputTab)
        self.outputTabLayout.setContentsMargins(0, 0, 0, 0)
        self.outputTabLayout.setObjectName("outputTabLayout")
        self.outputWidget = QtWidgets.QPlainTextEdit(self.outputTab)
        self.outputWidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.outputWidget.setTabChangesFocus(True)
        self.outputWidget.setUndoRedoEnabled(False)
        self.outputWidget.setReadOnly(True)
        self.outputWidget.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByKeyboard
            | QtCore.Qt.LinksAccessibleByMouse
            | QtCore.Qt.TextBrowserInteraction
            | QtCore.Qt.TextSelectableByKeyboard
            | QtCore.Qt.TextSelectableByMouse
        )
        self.outputWidget.setFont(MONOSPACE_FONT)
        self.outputWidget.setObjectName("outputWidget")
        self.outputTabLayout.addWidget(self.outputWidget)

        # Tab widget
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.addTab(self.resultsTab, "")
        self.tabWidget.addTab(self.outputTab, "")
        self.tabWidget.setCurrentIndex(0)
        self.centralLayout.addWidget(self.tabWidget)

        # Actions
        self.actionCollapse_all = QtWidgets.QAction(self)
        self.actionCollapse_all.setIcon(ICONS["COLLAPSE"])
        self.actionCollapse_all.setObjectName("actionCollapse_all")
        self.actionExpand_all = QtWidgets.QAction(self)
        self.actionExpand_all.setIcon(ICONS["EXPAND"])
        self.actionExpand_all.setObjectName("actionExpand_all")
        self.actionRun = QtWidgets.QAction(self)
        self.actionRun.setIcon(ICONS["START"])
        self.actionRun.setObjectName("actionRun")
        self.actionAbort = QtWidgets.QAction(self)
        self.actionAbort.setIcon(ICONS["STOP"])
        self.actionAbort.setObjectName("actionAbort")
        self.actionQuit = QtWidgets.QAction(self)
        self.actionQuit.setIcon(ICONS["ABORT"])
        self.actionQuit.setObjectName("actionQuit")
        self.actionConfigure = QtWidgets.QAction(self)
        self.actionConfigure.setIcon(ICONS["CONFIG"])
        self.actionConfigure.setObjectName("actionConfigure")
        self.actionLine_profiler_documentation = QtWidgets.QAction(self)
        self.actionLine_profiler_documentation.setIcon(ICONS["HELP"])
        self.actionLine_profiler_documentation.setObjectName(
            "actionLine_profiler_documentation"
        )
        self.actionAbout_Qt = QtWidgets.QAction(self)
        self.actionAbout_Qt.setIcon(ICONS["QT"])
        self.actionAbout_Qt.setObjectName("actionAbout_Qt")

        # Menu bar
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        # Profiling menu
        self.menuProfiling = QtWidgets.QMenu(self.menubar)
        self.menuProfiling.setObjectName("menuProfiling")
        self.menuProfiling.addAction(self.actionConfigure)
        self.menuProfiling.addSeparator()
        self.menuProfiling.addAction(self.actionRun)
        self.menuProfiling.addAction(self.actionAbort)
        self.menuProfiling.addSeparator()
        self.menuProfiling.addAction(self.actionQuit)
        self.menubar.addAction(self.menuProfiling.menuAction())

        # Display Menu
        self.menuDisplay = QtWidgets.QMenu(self.menubar)
        self.menuDisplay.setObjectName("menuDisplay")
        self.menuDisplay.addAction(self.actionCollapse_all)
        self.menuDisplay.addAction(self.actionExpand_all)
        self.menubar.addAction(self.menuDisplay.menuAction())

        # Help Menu
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuHelp.addAction(self.actionLine_profiler_documentation)
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
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionCollapse_all)
        self.toolBar.addAction(self.actionExpand_all)

        # Statusbar
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.statusbar_running_indicator = QtWidgets.QLabel()
        self.statusbar_running_indicator.setPixmap(PIXMAPS["RUNNING"])
        self.statusbar_running_indicator.setVisible(False)
        self.statusbar_running_indicator_timer = QtCore.QTimer(self)
        self.statusbar_running_indicator_timer.timeout.connect(
            lambda: self.statusbar_running_indicator.setVisible(
                not self.statusbar_running_indicator.isVisible()
            )
        )
        self.statusbar.addPermanentWidget(self.statusbar_running_indicator)

        # Finalization
        self.retranslate_ui()
        self.set_running_state(False)

    def connect(self):
        QtCore.QMetaObject.connectSlotsByName(self)
        self.actionCollapse_all.triggered.connect(self.resultsTreeWidget.collapseAll)
        self.actionExpand_all.triggered.connect(self.resultsTreeWidget.expandAll)
        self.actionAbort.triggered.connect(self.kernprof_run.kill)
        self.actionQuit.triggered.connect(QtWidgets.QApplication.instance().quit)
        self.actionLine_profiler_documentation.triggered.connect(
            lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(LINE_PROFILER_DOC_URL))
        )
        self.actionAbout_Qt.triggered.connect(QtWidgets.QApplication.aboutQt)
        self.kernprof_run.output_text.connect(self.append_log_text)
        self.kernprof_run.output_error.connect(self.append_log_error)

    def retranslate_ui(self):
        self.update_window_title()
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.resultsTab), _("Profiling results"),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.outputTab), _("Script Output"),
        )
        self.menuDisplay.setTitle(_("&Display"))
        self.menuProfiling.setTitle(_("&Profiling"))
        self.menuHelp.setTitle(_("&Help"))
        self.toolBar.setWindowTitle(_("toolBar"))
        self.actionCollapse_all.setText(_("&Collapse all"))
        self.actionExpand_all.setText(_("&Expand all"))
        self.actionRun.setText(_("&Profile"))
        self.actionRun.setShortcut(_("F5"))
        self.actionAbort.setText(_("&Stop"))
        self.actionAbort.setShortcut(_("F6"))
        self.actionQuit.setText(_("&Quit"))
        self.actionQuit.setShortcut(_("Ctrl+Q"))
        self.actionConfigure.setText(_("&Configuration..."))
        self.actionConfigure.setToolTip(_("Configuration"))
        self.actionConfigure.setShortcut(_("Ctrl+O"))
        self.actionLine_profiler_documentation.setText(
            _("&Line profiler documentation...")
        )
        self.actionLine_profiler_documentation.setShortcut(_("F1"))
        self.actionAbout_Qt.setText(_("&About Qt..."))

    def update_window_title(self):
        title = _("Line Profiler GUI")
        if self.config.script:
            title += f" - {self.config.script}"
        self.setWindowTitle(title)

    @QtCore.Slot()
    def on_actionConfigure_triggered(self):
        Ui_ConfigDialog(self, self.config).exec()
        self.update_window_title()

    @QtCore.Slot()
    def on_actionRun_triggered(self):
        # Configuration dialog in case of invalid config
        if not self.config.isvalid:
            self.on_actionConfigure_triggered()
            if not self.config.isvalid:
                return

        # Start process
        self.outputWidget.clear()
        process = self.kernprof_run.prepare()
        process.stateChanged.connect(self.set_running_state)
        process.finished.connect(self.process_finished)
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
        else:
            self.unsetCursor()
            self.statusbar_running_indicator_timer.stop()

    @QtCore.Slot(str)
    def append_log_text(self, text):
        self.outputWidget.appendPlainText(text)

    @QtCore.Slot(str)
    def append_log_error(self, text):
        self.outputWidget.appendHtml(f'<p style="color:red;white-space:pre">{text}</p>')

    @QtCore.Slot()
    def process_finished(self):
        self.resultsTreeWidget.load_data(self.config.stats)


def create_app(options):
    # Create Qt application
    app = QtWidgets.QApplication([])
    _icons_factory()

    # Create main window
    win = UI_MainWindow()
    win.show()
    if options.script:
        win.config.build_simple_config(options.script, options.args, options.outfile)
        win.update_window_title()
        if options.run:
            win.on_actionRun_triggered()
        else:
            win.on_actionConfigure_triggered()
    else:
        win.on_actionConfigure_triggered()

    # Keep a reference to the win object to avoid destruction
    app.win = win

    return app
