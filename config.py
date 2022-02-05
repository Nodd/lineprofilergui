import os
import shutil
from pathlib import Path

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Qt
import qtpy.compat as qtcompat


from utils import translate as _


class Config:
    def __init__(self):
        self.wdir = None
        self.script = None
        self.arguments = ""
        self.env = {}
        self.stats = None
        self.kernprof = None

    def build_simple_config(self, script, arguments):
        self.wdir = self.default_wdir
        self.script = script
        self.arguments = arguments
        self.env = {}
        self.stats = self.default_stats
        self.kernprof = self.default_kernprof

    @property
    def default_wdir(self):
        return os.getcwd()

    @property
    def default_stats(self):
        return self.default_stats_for_script(self.script)

    def default_stats_for_script(self, script):
        if not script:
            return None
        else:
            return os.fspath(Path(script).with_suffix(".lprof"))

    @property
    def default_kernprof(self):
        return shutil.which("kernprof")


class Ui_ConfigDialog(QtWidgets.QDialog):
    def __init__(self, parent, config):
        QtWidgets.QDialog.__init__(self)
        self.setup_ui()

        self.config = config
        self.config_to_ui()

    def config_to_ui(self):
        self.wdirWidget.setText(self.config.wdir)
        self.scriptWidget.setText(self.config.script)
        self.argumentsWidget.setText(self.config.arguments)
        self.envWidgets.setText(
            ";".join(f"{key}={value}" for key, value in self.config.env.items())
        )
        self.statsWidget.setText(self.config.stats)
        self.kernprofWidget.setText(self.config.kernprof)

        self.update()

    def ui_to_config(self):
        self.config.wdir = self.wdirWidget.text() or None
        self.config.script = self.scriptWidget.text() or None
        self.config.arguments = self.argumentsWidget.text()
        self.config.env = {}
        for var in self.envWidgets.text().split(";"):
            if var:
                key, value = var.split("=")
                self.config.env[key] = value
        self.config.stats = self.statsWidget.text() or None
        self.config.kernprof = self.kernprofWidget.text() or None

    def update(self):
        self.wdirWidget.setPlaceholderText(self.config.default_wdir)
        self.statsWidget.setPlaceholderText(
            self.config.default_stats_for_script(self.scriptWidget.text())
        )
        self.kernprofWidget.setPlaceholderText(self.config.default_kernprof)

    def setup_ui(self):
        # Dialog
        self.setObjectName("self")
        self.resize(600, 186)
        self.setModal(True)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.configLayout = QtWidgets.QFormLayout(self)
        self.configLayout.setObjectName("configLayout")

        # Working directory
        self.wdirLabel = QtWidgets.QLabel(self)
        self.wdirLabel.setObjectName("wdirLabel")
        self.configLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.wdirLabel)
        self.wdirLayout = QtWidgets.QHBoxLayout()
        self.wdirLayout.setObjectName("wdirLayout")
        self.wdirWidget = QtWidgets.QLineEdit(self)
        self.wdirWidget.setObjectName("wdirWidget")
        self.wdirLayout.addWidget(self.wdirWidget)
        self.wdirButton = QtWidgets.QPushButton(self)
        self.wdirButton.setObjectName("wdirButton")
        self.wdirLayout.addWidget(self.wdirButton)
        self.configLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.wdirLayout)

        # Python script
        self.scriptLabel = QtWidgets.QLabel(self)
        self.scriptLabel.setObjectName("scriptLabel")
        self.configLayout.setWidget(
            1, QtWidgets.QFormLayout.LabelRole, self.scriptLabel
        )
        self.scriptLayout = QtWidgets.QHBoxLayout()
        self.scriptLayout.setObjectName("scriptLayout")
        self.scriptWidget = QtWidgets.QLineEdit(self)
        self.scriptWidget.setObjectName("scriptWidget")
        self.scriptLayout.addWidget(self.scriptWidget)
        self.scriptButton = QtWidgets.QPushButton(self)
        self.scriptButton.setObjectName("scriptButton")
        self.scriptLayout.addWidget(self.scriptButton)
        self.configLayout.setLayout(
            1, QtWidgets.QFormLayout.FieldRole, self.scriptLayout
        )

        # Scripts arguments
        self.argumentsLabel = QtWidgets.QLabel(self)
        self.argumentsLabel.setObjectName("argumentsLabel")
        self.configLayout.setWidget(
            2, QtWidgets.QFormLayout.LabelRole, self.argumentsLabel
        )
        self.argumentsWidget = QtWidgets.QLineEdit(self)
        font = QtGui.QFont("Monospace")
        font.setStyleHint(QtGui.QFont.Monospace)
        self.argumentsWidget.setFont(font)
        self.argumentsWidget.setObjectName("argumentsWidget")
        self.configLayout.setWidget(
            2, QtWidgets.QFormLayout.FieldRole, self.argumentsWidget
        )

        # Environment variables
        self.envLabel = QtWidgets.QLabel(self)
        self.envLabel.setObjectName("envLabel")
        self.configLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.envLabel)
        self.envWidgets = QtWidgets.QLineEdit(self)
        self.envWidgets.setObjectName("envWidgets")
        self.configLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.envWidgets)

        # Stats filename
        self.statsLabel = QtWidgets.QLabel(self)
        self.statsLabel.setObjectName("statsLabel")
        self.configLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.statsLabel)
        self.statsLayout = QtWidgets.QHBoxLayout()
        self.statsLayout.setObjectName("statsLayout")
        self.statsWidget = QtWidgets.QLineEdit(self)
        self.statsWidget.setObjectName("statsWidget")
        self.statsLayout.addWidget(self.statsWidget)
        self.statsButton = QtWidgets.QPushButton(self)
        self.statsButton.setObjectName("statsButton")
        self.statsLayout.addWidget(self.statsButton)
        self.configLayout.setLayout(
            4, QtWidgets.QFormLayout.FieldRole, self.statsLayout
        )

        # kernprof executable
        self.kernprofLabel = QtWidgets.QLabel(self)
        self.kernprofLabel.setObjectName("kernprofLabel")
        self.configLayout.setWidget(
            5, QtWidgets.QFormLayout.LabelRole, self.kernprofLabel
        )
        self.kernprofLayout = QtWidgets.QHBoxLayout()
        self.kernprofLayout.setObjectName("kernprofLayout")
        self.kernprofWidget = QtWidgets.QLineEdit(self)
        self.kernprofWidget.setObjectName("kernprofWidget")
        self.kernprofLayout.addWidget(self.kernprofWidget)
        self.kernprofButton = QtWidgets.QPushButton(self)
        self.kernprofButton.setObjectName("kernprofButton")
        self.kernprofLayout.addWidget(self.kernprofButton)
        self.configLayout.setLayout(
            5, QtWidgets.QFormLayout.FieldRole, self.kernprofLayout
        )

        # Buttons
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.configLayout.setWidget(
            6, QtWidgets.QFormLayout.SpanningRole, self.buttonBox
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Finalization
        self.retranslate_ui()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslate_ui(self):
        self.setWindowTitle(_("Line profiler configuration"))
        self.wdirLabel.setText(_("Working directory"))
        self.wdirButton.setText(_("Select..."))
        self.scriptLabel.setText(_("Python script"))
        self.scriptButton.setText(_("Select..."))
        self.argumentsLabel.setText(_("Script arguments"))
        self.envLabel.setText(_("Environment variables"))
        self.statsLabel.setText(_("Stats filename"))
        self.statsButton.setText(_("Select..."))
        self.kernprofLabel.setText(_("<tt>kernprof</tt> path"))
        self.kernprofButton.setText(_("Select..."))

    @QtCore.Slot()
    def accept(self):
        self.ui_to_config()
        QtWidgets.QDialog.accept(self)

    @QtCore.Slot()
    def on_wdirButton_clicked(self):
        filename = qtcompat.getexistingdirectory(
            self, _("Select Python script"), self.wdirWidget.text(),
        )
        if filename:
            self.wdirWidget.setText(filename)

    @QtCore.Slot()
    def on_scriptButton_clicked(self):
        filename, _selfilter = qtcompat.getopenfilename(
            self,
            _("Select Python script"),
            self.scriptWidget.text(),
            _("Python scripts") + " (*.py ; *.pyw)",
        )
        if filename:
            path = Path(filename)
            try:
                path = path.relative_to(self.config.wdir)
            except ValueError:
                pass
            else:
                filename = os.fspath(path)
            self.scriptWidget.setText(filename)

    @QtCore.Slot()
    def on_statsButton_clicked(self):
        filename, _selfilter = qtcompat.getsavefilename(
            self,
            _("Select stats filename"),
            self.statsWidget.text(),
            _("Stats filename") + " (* ; *.lprof)",
        )
        if filename:
            self.statsWidget.setText(filename)

    @QtCore.Slot()
    def on_kernprofButton_clicked(self):
        filename, _selfilter = qtcompat.getopenfilename(
            self,
            _("Select kernprof executable"),
            self.kernprofWidget.text() or self.config.default_kernprof,
            _("kernprof executable") + " (kernprof*)",
        )
        if filename:
            self.kernprofWidget.setText(filename)

    @QtCore.Slot(str)
    def on_scriptWidget_textChanged(self, text):
        # Update placeholder text
        self.update()
