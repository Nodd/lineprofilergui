from qtpy import QtCore, QtWidgets

from .utils import translate as _

EDITOR_COMMAND_EXAMPLES = [
    "",
    "code --goto {file}:{line}",
    '"C:\\\\Program Files (x86)\\\\Notepad++\\\\Notepad++" {file} -n{line}',
    "vim +{line} {file}",
]


class UI_SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.resize(600, 200)
        self.setModal(True)
        self.mainLayout = QtWidgets.QVBoxLayout(self)

        # Editor command
        self.editorCommandGroupBox = QtWidgets.QGroupBox(self)
        self.editorCommandLayout = QtWidgets.QVBoxLayout(self.editorCommandGroupBox)
        self.editorCommandLayout.setObjectName("editorCommandLayout")
        self.editorCommandLabel = QtWidgets.QLabel(self.editorCommandGroupBox)
        self.editorCommandLabel.setWordWrap(True)
        self.editorCommandLayout.addWidget(self.editorCommandLabel)
        self.editorCommandCombo = QtWidgets.QComboBox(self.editorCommandGroupBox)
        self.editorCommandCombo.setEditable(True)
        for cmd in EDITOR_COMMAND_EXAMPLES:
            self.editorCommandCombo.addItem(cmd)
        self.editorCommandLayout.addWidget(self.editorCommandCombo)
        self.mainLayout.addWidget(self.editorCommandGroupBox)

        # Columns visibility
        self.columnsGroupBox = QtWidgets.QGroupBox(self)
        self.columnsLayout = QtWidgets.QHBoxLayout(self.columnsGroupBox)
        self.checkBox_1 = QtWidgets.QCheckBox(self.columnsGroupBox)
        self.checkBox_1.setChecked(True)
        self.columnsLayout.addWidget(self.checkBox_1)
        self.checkBox_2 = QtWidgets.QCheckBox(self.columnsGroupBox)
        self.checkBox_2.setChecked(True)
        self.columnsLayout.addWidget(self.checkBox_2)
        self.checkBox_3 = QtWidgets.QCheckBox(self.columnsGroupBox)
        self.checkBox_3.setChecked(True)
        self.columnsLayout.addWidget(self.checkBox_3)
        self.checkBox_4 = QtWidgets.QCheckBox(self.columnsGroupBox)
        self.checkBox_4.setChecked(True)
        self.columnsLayout.addWidget(self.checkBox_4)
        self.checkBox_5 = QtWidgets.QCheckBox(self.columnsGroupBox)
        self.checkBox_5.setChecked(True)
        self.columnsLayout.addWidget(self.checkBox_5)
        self.mainLayout.addWidget(self.columnsGroupBox)

        # Button box
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.mainLayout.addWidget(self.buttonBox)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Spacer
        spacerItem = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.mainLayout.addItem(spacerItem)

        self.retranslate_ui()
        self.reject()  # Load settings values

    def retranslate_ui(self):
        self.setWindowTitle(_("Line Profiler GUI - Settings"))
        self.editorCommandGroupBox.setTitle(_("Open file"))
        self.editorCommandLabel.setText(
            _(
                "Command to run when a line is double-clicked in the profiling result panel."
                " <tt>{file}</tt> will be replaced by the stringified filename,"
                " and <tt>{line}</tt> will be replaced by the line number."
            )
        )
        self.columnsGroupBox.setTitle(_("Visible colums"))
        self.checkBox_1.setText(_("Line #"))
        self.checkBox_2.setText(_("Hits"))
        self.checkBox_3.setText(_("Time (ms)"))
        self.checkBox_4.setText(_("Per Hit (ms)"))
        self.checkBox_5.setText(_("% Time"))

    @QtCore.Slot()
    def accept(self):
        settings = QtCore.QSettings()
        settings.setValue("editorCommand", self.editorCommandCombo.currentText())
        settings.setValue("column1Visible", self.checkBox_1.isChecked())
        settings.setValue("column2Visible", self.checkBox_2.isChecked())
        settings.setValue("column3Visible", self.checkBox_3.isChecked())
        settings.setValue("column4Visible", self.checkBox_4.isChecked())
        settings.setValue("column5Visible", self.checkBox_5.isChecked())
        QtWidgets.QDialog.accept(self)

        self.parent()

    @QtCore.Slot()
    def reject(self):
        settings = QtCore.QSettings()
        self.editorCommandCombo.setCurrentText(settings.value("editorCommand", ""))
        self.checkBox_1.setChecked(settings.value("column1Visible", True, bool))
        self.checkBox_2.setChecked(settings.value("column2Visible", True, bool))
        self.checkBox_3.setChecked(settings.value("column3Visible", True, bool))
        self.checkBox_4.setChecked(settings.value("column4Visible", True, bool))
        self.checkBox_5.setChecked(settings.value("column5Visible", True, bool))
        QtWidgets.QDialog.reject(self)
