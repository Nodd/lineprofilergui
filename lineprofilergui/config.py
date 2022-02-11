import os
import shutil
import shlex
from pathlib import Path
import tempfile
from functools import cached_property

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Qt
import qtpy.compat as qtcompat


from .utils import translate as _, MONOSPACE_FONT, PIXMAPS, ICONS


class Config:
    def __init__(self):
        self.config_wdir = None
        self.script = None
        self.args = ""
        self.warmup = None
        self.stats_tmp = True
        self.config_env = ""
        self.config_stats = None
        self.config_kernprof = None

        self._temp_dir_obj = None
        self._temp_dir = None

    @cached_property
    def temp_dir(self):
        self._temp_dir_obj = tempfile.TemporaryDirectory(
            prefix="lineprofilergui_", suffix="_lprof"
        )
        print(self._temp_dir_obj.name)
        return self._temp_dir_obj.name

    def __del__(self):
        if self._temp_dir_obj:
            self._temp_dir_obj.cleanup()

    @property
    def wdir(self):
        return self.config_wdir or self.default_wdir

    @property
    def default_wdir(self):
        return os.getcwd()

    @property
    def isvalid_wdir(self):
        return not self.config_wdir or Path(self.config_wdir).is_dir()

    @property
    def isvalid_script(self):
        if not self.script:
            return False
        # Script file must exist, either as an ablsolute path,
        # or relative to the working directory
        script_path = Path(self.config_wdir or "") / Path(self.script)
        return script_path.is_file()

    @property
    def isvalid_warmup(self):
        if not self.warmup:
            return True
        # Script file must exist, either as an ablsolute path,
        # or relative to the working directory
        warmup_path = Path(self.config_wdir or "") / Path(self.warmup)
        return warmup_path.is_file()

    @property
    def stats(self):
        if self.stats_tmp:
            return os.fspath(Path(self.temp_dir) / (Path(self.script).stem + ".lprof"))
        else:
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
        if not self.config_stats or self.stats_tmp:
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
            and self.isvalid_warmup
            and self.isvalid_stats
            and self.isvalid_kernprof
            and self.isvalid_env
        )


class Ui_ConfigDialog(QtWidgets.QDialog):
    def __init__(self, parent, config):
        self.config = config

        super().__init__(parent)
        self.setup_ui()

        self.config_to_ui()

    def config_to_ui(self):
        self.wdirWidget.setText(self.config.config_wdir)
        self.scriptWidget.setText(self.config.script)
        self.argsWidget.setText(self.config.args)
        self.warmupWidget.setText(self.config.warmup)
        self.envWidget.setText(self.config.config_env)
        self.statsWidget.setText(self.config.config_stats)
        self.statsTmp.setChecked(self.config.stats_tmp)
        self.kernprofWidget.setText(self.config.config_kernprof)

        self.update()

    def ui_to_config(self, config=None):
        if config is None:
            config = self.config
        config.config_wdir = self.wdirWidget.text() or None
        config.script = self.scriptWidget.text() or None
        config.args = self.argsWidget.text()
        config.warmup = self.warmupWidget.text() or None
        config.config_env = self.envWidget.text()
        config.config_stats = self.statsWidget.text() or None
        config.stats_tmp = self.statsTmp.isChecked()
        config.config_kernprof = self.kernprofWidget.text() or None

    def update(self):
        self.wdirWidget.setPlaceholderText(self.config.default_wdir)
        self.kernprofWidget.setPlaceholderText(self.config.default_kernprof)
        self.on_wdirWidget_textChanged("")
        self.on_scriptWidget_textChanged("")
        self.on_warmupWidget_textChanged("")
        self.on_statsWidget_textChanged("")
        self.on_kernprofWidget_textChanged("")
        self.on_envWidget_textChanged("")

    def update_stats_placeholder(self):
        if not self.config.stats_tmp:
            self.statsWidget.setPlaceholderText(
                self.config.default_stats_for_script(self.scriptWidget.text())
            )
        else:
            self.statsWidget.setPlaceholderText("")

    def update_stats_enabled(self):
        stats_tmp = self.statsTmp.isChecked()
        self.statsWidget.setEnabled(not stats_tmp)
        self.statsButton.setEnabled(not stats_tmp)

    def setup_ui(self):
        # Dialog
        self.setObjectName("self")
        self.resize(600, 186)
        self.setModal(True)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.configLayout = QtWidgets.QFormLayout(self)
        self.configLayout.setObjectName("configLayout")
        row = 0

        # Working directory
        self.wdirLabel = QtWidgets.QLabel(self)
        self.configLayout.setWidget(
            row, QtWidgets.QFormLayout.LabelRole, self.wdirLabel
        )
        self.wdirLayout = QtWidgets.QHBoxLayout()
        self.wdirWidget = QtWidgets.QLineEdit(self)
        self.wdirWidget.setObjectName("wdirWidget")
        self.wdirLayout.addWidget(self.wdirWidget)
        self.wdirStatusLabel = QtWidgets.QLabel(self)
        self.wdirStatusLabel.setPixmap(PIXMAPS["NOK"])
        self.wdirLayout.addWidget(self.wdirStatusLabel)
        self.wdirButton = QtWidgets.QPushButton(self)
        self.wdirButton.setIcon(ICONS["DIRECTORY"])
        self.wdirButton.setObjectName("wdirButton")
        self.wdirLayout.addWidget(self.wdirButton)
        self.configLayout.setLayout(
            row, QtWidgets.QFormLayout.FieldRole, self.wdirLayout
        )
        self.wdirWidget.setValidator(ConfigValidator(self, "wdir"))
        row += 1

        # Python script
        self.scriptLabel = QtWidgets.QLabel(self)
        self.configLayout.setWidget(
            row, QtWidgets.QFormLayout.LabelRole, self.scriptLabel
        )
        self.scriptLayout = QtWidgets.QHBoxLayout()
        self.scriptWidget = QtWidgets.QLineEdit(self)
        self.scriptWidget.setObjectName("scriptWidget")
        self.scriptLayout.addWidget(self.scriptWidget)
        self.scriptStatusLabel = QtWidgets.QLabel(self)
        self.scriptStatusLabel.setPixmap(PIXMAPS["NOK"])
        self.scriptLayout.addWidget(self.scriptStatusLabel)
        self.scriptButton = QtWidgets.QPushButton(self)
        self.scriptButton.setIcon(ICONS["READFILE"])
        self.scriptButton.setObjectName("scriptButton")
        self.scriptLayout.addWidget(self.scriptButton)
        self.configLayout.setLayout(
            row, QtWidgets.QFormLayout.FieldRole, self.scriptLayout
        )
        self.scriptWidget.setValidator(ConfigValidator(self, "script"))
        row += 1

        # Scripts args
        self.argsLabel = QtWidgets.QLabel(self)
        self.configLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.argsLabel)
        self.argsWidget = QtWidgets.QLineEdit(self)
        self.argsWidget.setFont(MONOSPACE_FONT)
        self.argsWidget.setObjectName("argsWidget")
        self.configLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.argsWidget)
        row += 1

        # Python script
        self.warmupLabel = QtWidgets.QLabel(self)
        self.configLayout.setWidget(
            row, QtWidgets.QFormLayout.LabelRole, self.warmupLabel
        )
        self.warmupLayout = QtWidgets.QHBoxLayout()
        self.warmupWidget = QtWidgets.QLineEdit(self)
        self.warmupWidget.setObjectName("warmupWidget")
        self.warmupLayout.addWidget(self.warmupWidget)
        self.warmupStatusLabel = QtWidgets.QLabel(self)
        self.warmupStatusLabel.setPixmap(PIXMAPS["NOK"])
        self.warmupLayout.addWidget(self.warmupStatusLabel)
        self.warmupButton = QtWidgets.QPushButton(self)
        self.warmupButton.setIcon(ICONS["READFILE"])
        self.warmupButton.setObjectName("warmupButton")
        self.warmupLayout.addWidget(self.warmupButton)
        self.configLayout.setLayout(
            row, QtWidgets.QFormLayout.FieldRole, self.warmupLayout
        )
        self.warmupWidget.setValidator(ConfigValidator(self, "warmup"))
        row += 1

        # Environment variables
        self.envLabel = QtWidgets.QLabel(self)
        self.configLayout.setWidget(row, QtWidgets.QFormLayout.LabelRole, self.envLabel)
        self.envLayout = QtWidgets.QHBoxLayout()
        self.envWidget = QtWidgets.QLineEdit(self)
        self.envWidget.setObjectName("envWidget")
        self.envLayout.addWidget(self.envWidget)
        self.envStatusLabel = QtWidgets.QLabel(self)
        self.envStatusLabel.setPixmap(PIXMAPS["NOK"])
        self.envLayout.addWidget(self.envStatusLabel)
        self.configLayout.setLayout(
            row, QtWidgets.QFormLayout.FieldRole, self.envLayout
        )
        self.envWidget.setValidator(ConfigValidator(self, "env"))
        row += 1

        # Stats filename
        self.statsLabel = QtWidgets.QLabel(self)
        self.configLayout.setWidget(
            row, QtWidgets.QFormLayout.LabelRole, self.statsLabel
        )
        self.statsLayout = QtWidgets.QHBoxLayout()
        self.statsTmp = QtWidgets.QCheckBox(self)
        self.statsTmp.setObjectName("statsTmp")
        self.statsLayout.addWidget(self.statsTmp)
        self.statsWidget = QtWidgets.QLineEdit(self)
        self.statsWidget.setObjectName("statsWidget")
        self.statsLayout.addWidget(self.statsWidget)
        self.statsStatusLabel = QtWidgets.QLabel(self)
        self.statsStatusLabel.setPixmap(PIXMAPS["NOK"])
        self.statsLayout.addWidget(self.statsStatusLabel)
        self.statsButton = QtWidgets.QPushButton(self)
        self.statsButton.setIcon(ICONS["BLANKFILE"])
        self.statsButton.setObjectName("statsButton")
        self.statsLayout.addWidget(self.statsButton)
        self.configLayout.setLayout(
            row, QtWidgets.QFormLayout.FieldRole, self.statsLayout
        )
        self.statsWidget.setValidator(ConfigValidator(self, "stats"))
        row += 1

        # kernprof executable
        self.kernprofLabel = QtWidgets.QLabel(self)
        self.configLayout.setWidget(
            row, QtWidgets.QFormLayout.LabelRole, self.kernprofLabel
        )
        self.kernprofLayout = QtWidgets.QHBoxLayout()
        self.kernprofWidget = QtWidgets.QLineEdit(self)
        self.kernprofWidget.setObjectName("kernprofWidget")
        self.kernprofLayout.addWidget(self.kernprofWidget)
        self.kernprofStatusLabel = QtWidgets.QLabel(self)
        self.kernprofStatusLabel.setPixmap(PIXMAPS["NOK"])
        self.kernprofLayout.addWidget(self.kernprofStatusLabel)
        self.kernprofButton = QtWidgets.QPushButton(self)
        self.kernprofButton.setIcon(ICONS["READFILE"])
        self.kernprofButton.setObjectName("kernprofButton")
        self.kernprofLayout.addWidget(self.kernprofButton)
        self.configLayout.setLayout(
            row, QtWidgets.QFormLayout.FieldRole, self.kernprofLayout
        )
        self.kernprofWidget.setValidator(ConfigValidator(self, "kernprof"))
        row += 1

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
            row, QtWidgets.QFormLayout.SpanningRole, self.buttonBox
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        row += 1

        # Finalization
        self.retranslate_ui()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslate_ui(self):
        self.setWindowTitle(_("Line Profiler GUI - Profiling configuration"))
        self.wdirLabel.setText(_("Working directory"))
        self.wdirButton.setText(_("Select..."))
        self.scriptLabel.setText(_("Python script"))
        self.scriptButton.setText(_("Select..."))
        self.warmupLabel.setText(_("Warm up script"))
        self.warmupButton.setText(_("Select..."))
        self.argsLabel.setText(_("Script args"))
        self.envLabel.setText(_("Environment variables"))
        self.statsLabel.setText(_("Stats filename"))
        self.statsTmp.setText(_("Temporary file"))
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
        self.parent().profile()

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
        indicator.setVisible(not widget.hasAcceptableInput())
        self.update_profileButton_enabled()

    @QtCore.Slot(str)
    def on_wdirWidget_textChanged(self, text):
        self.display_status(self.wdirWidget, self.wdirStatusLabel)

    @QtCore.Slot(str)
    def on_scriptWidget_textChanged(self, text):
        self.display_status(self.scriptWidget, self.scriptStatusLabel)
        self.update_stats_placeholder()

    @QtCore.Slot(str)
    def on_warmupWidget_textChanged(self, text):
        self.display_status(self.warmupWidget, self.warmupStatusLabel)

    @QtCore.Slot(str)
    def on_statsWidget_textChanged(self, text):
        self.display_status(self.statsWidget, self.statsStatusLabel)

    @QtCore.Slot(int)
    def on_statsTmp_stateChanged(self, state):
        self.update_stats_enabled()
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
    def on_warmupButton_clicked(self):
        filename, _selfilter = qtcompat.getopenfilename(
            self,
            _("Select Python warmup script"),
            self.warmupWidget.text(),
            _("Python scripts") + " (*.py ; *.pyw)",
        )
        if filename:
            self.warmupWidget.setText(filename)

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
        super().__init__()
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
