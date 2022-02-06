import os
import shutil
import shlex
from pathlib import Path

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Qt
import qtpy.compat as qtcompat


from .utils import translate as _, MONOSPACE_FONT, PIXMAPS, ICONS


class Config:
    def __init__(self):
        self.config_wdir = None
        self.script = None
        self.args = ""
        self.config_env = ""
        self.config_stats = None
        self.config_kernprof = None

    def build_simple_config(self, script, args="", stats=None):
        self.script = script
        self.args = args
        self.config_stats = stats

        self.config_wdir = None
        self.config_env = ""
        self.config_kernprof = None

    @property
    def wdir(self):
        return self.config_wdir or self.default_wdir

    @property
    def default_wdir(self):
        return os.getcwd()

    @property
    def isvalid_wdir(self):
        return not self.config_wdir or Path(self.config_wdir).isdir()

    @property
    def isvalid_script(self):
        if not self.script:
            return False
        # Script file must exist, either as an ablsolute path,
        # or relative to the working directory
        script_path = Path(self.config_wdir or "") / Path(self.script)
        return script_path.is_file()

    @property
    def stats(self):
        return self.config_stats or self.default_stats

    @property
    def default_stats(self):
        return self.default_stats_for_script(self.script)

    def default_stats_for_script(self, script):
        if not script:
            return None
        else:
            return os.fspath(Path(script).with_suffix(".lprof"))

    @property
    def isvalid_stats(self):
        if not self.config_stats:
            return True
        return (
            not self.config_stats.endswith(("/", "\\"))
            and Path(self.config_stats).parent.is_dir()
        )

    @property
    def kernprof(self):
        return self.config_kernprof or self.default_kernprof

    @property
    def default_kernprof(self):
        return shutil.which("kernprof")

    @property
    def isvalid_kernprof(self):
        default_kernprof_path = not self.config_kernprof and self.default_kernprof
        return default_kernprof_path or Path(self.config_kernprof).is_file()

    @property
    def env(self):
        env = {}
        for var in shlex.split(self.config_env):
            name, value = var.split("=", maxsplit=1)
            env[name] = value
        return env

    @property
    def isvalid_env(self):
        try:
            self.env
        except ValueError:
            return False
        return True

    @property
    def isvalid(self):
        return bool(
            self.isvalid_wdir
            and self.isvalid_script
            and self.isvalid_stats
            and self.isvalid_kernprof
            and self.isvalid_env
        )


class Ui_ConfigDialog(QtWidgets.QDialog):
    def __init__(self, parent, config):
        self.config = config

        QtWidgets.QDialog.__init__(self, parent)
        self.setup_ui()

        self.config_to_ui()

    def config_to_ui(self):
        self.wdirWidget.setText(self.config.config_wdir)
        self.scriptWidget.setText(self.config.script)
        self.argsWidget.setText(self.config.args)
        self.envWidget.setText(self.config.config_env)
        self.statsWidget.setText(self.config.config_stats)
        self.kernprofWidget.setText(self.config.config_kernprof)

        self.update()

    def ui_to_config(self, config=None):
        if config is None:
            config = self.config
        config.config_wdir = self.wdirWidget.text() or None
        config.script = self.scriptWidget.text() or None
        config.args = self.argsWidget.text()
        config.config_env = self.envWidget.text()
        config.config_stats = self.statsWidget.text() or None
        config.config_kernprof = self.kernprofWidget.text() or None

    def update(self):
        self.wdirWidget.setPlaceholderText(self.config.default_wdir)
        self.update_stats_placeholder()
        self.kernprofWidget.setPlaceholderText(self.config.default_kernprof)
        self.on_wdirWidget_textChanged("")
        self.on_scriptWidget_textChanged("")
        self.on_statsWidget_textChanged("")
        self.on_kernprofWidget_textChanged("")
        self.on_envWidget_textChanged("")

    def update_stats_placeholder(self):
        self.statsWidget.setPlaceholderText(
            self.config.default_stats_for_script(self.scriptWidget.text())
        )

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
        self.configLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.wdirLabel)
        self.wdirLayout = QtWidgets.QHBoxLayout()
        self.wdirWidget = QtWidgets.QLineEdit(self)
        self.wdirWidget.setObjectName("wdirWidget")
        self.wdirLayout.addWidget(self.wdirWidget)
        self.wdirStatusLabel = QtWidgets.QLabel(self)
        self.wdirLayout.addWidget(self.wdirStatusLabel)
        self.wdirButton = QtWidgets.QPushButton(self)
        self.wdirButton.setIcon(ICONS["DIRECTORY"])
        self.wdirButton.setObjectName("wdirButton")
        self.wdirLayout.addWidget(self.wdirButton)
        self.configLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.wdirLayout)
        self.wdirWidget.setValidator(ConfigValidator(self, "wdir"))

        # Python script
        self.scriptLabel = QtWidgets.QLabel(self)
        self.configLayout.setWidget(
            1, QtWidgets.QFormLayout.LabelRole, self.scriptLabel
        )
        self.scriptLayout = QtWidgets.QHBoxLayout()
        self.scriptWidget = QtWidgets.QLineEdit(self)
        self.scriptWidget.setObjectName("scriptWidget")
        self.scriptLayout.addWidget(self.scriptWidget)
        self.scriptStatusLabel = QtWidgets.QLabel(self)
        self.scriptLayout.addWidget(self.scriptStatusLabel)
        self.scriptButton = QtWidgets.QPushButton(self)
        self.scriptButton.setIcon(ICONS["READFILE"])
        self.scriptButton.setObjectName("scriptButton")
        self.scriptLayout.addWidget(self.scriptButton)
        self.configLayout.setLayout(
            1, QtWidgets.QFormLayout.FieldRole, self.scriptLayout
        )
        self.scriptWidget.setValidator(ConfigValidator(self, "script"))

        # Scripts args
        self.argsLabel = QtWidgets.QLabel(self)
        self.configLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.argsLabel)
        self.argsWidget = QtWidgets.QLineEdit(self)
        self.argsWidget.setFont(MONOSPACE_FONT)
        self.argsWidget.setObjectName("argsWidget")
        self.configLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.argsWidget)

        # Environment variables
        self.envLabel = QtWidgets.QLabel(self)
        self.configLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.envLabel)
        self.envLayout = QtWidgets.QHBoxLayout()
        self.envWidget = QtWidgets.QLineEdit(self)
        self.envWidget.setObjectName("envWidget")
        self.envLayout.addWidget(self.envWidget)
        self.envStatusLabel = QtWidgets.QLabel(self)
        self.envLayout.addWidget(self.envStatusLabel)
        self.configLayout.setLayout(3, QtWidgets.QFormLayout.FieldRole, self.envLayout)
        self.envWidget.setValidator(ConfigValidator(self, "env"))

        # Stats filename
        self.statsLabel = QtWidgets.QLabel(self)
        self.configLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.statsLabel)
        self.statsLayout = QtWidgets.QHBoxLayout()
        self.statsWidget = QtWidgets.QLineEdit(self)
        self.statsWidget.setObjectName("statsWidget")
        self.statsLayout.addWidget(self.statsWidget)
        self.statsStatusLabel = QtWidgets.QLabel(self)
        self.statsLayout.addWidget(self.statsStatusLabel)
        self.statsButton = QtWidgets.QPushButton(self)
        self.statsButton.setIcon(ICONS["BLANKFILE"])
        self.statsButton.setObjectName("statsButton")
        self.statsLayout.addWidget(self.statsButton)
        self.configLayout.setLayout(
            4, QtWidgets.QFormLayout.FieldRole, self.statsLayout
        )
        self.statsWidget.setValidator(ConfigValidator(self, "stats"))

        # kernprof executable
        self.kernprofLabel = QtWidgets.QLabel(self)
        self.configLayout.setWidget(
            5, QtWidgets.QFormLayout.LabelRole, self.kernprofLabel
        )
        self.kernprofLayout = QtWidgets.QHBoxLayout()
        self.kernprofWidget = QtWidgets.QLineEdit(self)
        self.kernprofWidget.setObjectName("kernprofWidget")
        self.kernprofLayout.addWidget(self.kernprofWidget)
        self.kernprofStatusLabel = QtWidgets.QLabel(self)
        self.kernprofLayout.addWidget(self.kernprofStatusLabel)
        self.kernprofButton = QtWidgets.QPushButton(self)
        self.kernprofButton.setIcon(ICONS["READFILE"])
        self.kernprofButton.setObjectName("kernprofButton")
        self.kernprofLayout.addWidget(self.kernprofButton)
        self.configLayout.setLayout(
            5, QtWidgets.QFormLayout.FieldRole, self.kernprofLayout
        )
        self.kernprofWidget.setValidator(ConfigValidator(self, "kernprof"))

        # Buttons
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.profileButton = self.buttonBox.addButton(
            _("Profile"), QtWidgets.QDialogButtonBox.AcceptRole
        )
        self.profileButton.setObjectName("profileButton")
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel
        )
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
        self.argsLabel.setText(_("Script args"))
        self.envLabel.setText(_("Environment variables"))
        self.statsLabel.setText(_("Stats filename"))
        self.statsButton.setText(_("Select..."))
        self.kernprofLabel.setText(_("<tt>kernprof</tt> path"))
        self.kernprofButton.setText(_("Select..."))

    @QtCore.Slot()
    def accept(self):
        self.ui_to_config()
        QtWidgets.QDialog.accept(self)
        super().accept()

    @QtCore.Slot()
    def on_profileButton_clicked(self):
        self.accept()
        self.parent().on_actionRun_triggered()

    def update_profileButton_enabled(self):
        config = Config()
        self.ui_to_config(config)
        self.profileButton.setEnabled(config.isvalid)

    @QtCore.Slot()
    def on_wdirButton_clicked(self):
        filename = qtcompat.getexistingdirectory(
            self, _("Select Python script"), self.wdirWidget.text(),
        )
        if filename:
            self.wdirWidget.setText(filename)

    def display_status(self, widget, indicator):
        indicator.setPixmap(PIXMAPS["OK" if widget.hasAcceptableInput() else "NOK"])
        self.update_profileButton_enabled()

    @QtCore.Slot(str)
    def on_wdirWidget_textChanged(self, text):
        self.display_status(self.wdirWidget, self.wdirStatusLabel)

    @QtCore.Slot(str)
    def on_scriptWidget_textChanged(self, text):
        self.display_status(self.scriptWidget, self.scriptStatusLabel)
        self.update_stats_placeholder()

    @QtCore.Slot(str)
    def on_statsWidget_textChanged(self, text):
        self.display_status(self.statsWidget, self.statsStatusLabel)

    @QtCore.Slot(str)
    def on_kernprofWidget_textChanged(self, text):
        self.display_status(self.kernprofWidget, self.kernprofStatusLabel)

    @QtCore.Slot(str)
    def on_envWidget_textChanged(self, text):
        self.display_status(self.envWidget, self.envStatusLabel)

    @QtCore.Slot()
    def on_scriptButton_clicked(self):
        filename, _selfilter = qtcompat.getopenfilename(
            self,
            _("Select Python script"),
            self.scriptWidget.text(),
            _("Python scripts") + " (*.py ; *.pyw)",
        )
        if filename:
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


class ConfigValidator(QtGui.QValidator):
    def __init__(self, configDialog, widgetID):
        QtGui.QValidator.__init__(self)
        self.configDialog = configDialog
        self.widgetID = widgetID

    @QtCore.Slot(str, int)
    def validate(self, text, pos):
        config = Config()
        self.configDialog.ui_to_config(config)
        return (
            QtGui.QValidator.Acceptable
            if getattr(config, f"isvalid_{self.widgetID}")
            else QtGui.QValidator.Intermediate,
            text,
            pos,
        )
