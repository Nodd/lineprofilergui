import os
import shlex

from qtpy import QtCore

from utils import translate as _

LOCALE_CODEC = QtCore.QTextCodec.codecForLocale()


class KernprofRun(QtCore.QObject):
    output_text = QtCore.Signal(str)
    output_error = QtCore.Signal(str)

    def __init__(self, config):
        QtCore.QObject.__init__(self)
        self.config = config

        self.process = None
        self.p_args = None

    def prepare(self):
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(self.read_error)

        # TODO: manage env
        # self.process.setProcessEnvironment(processEnvironment)

        self.process.setWorkingDirectory(self.config.wdir)
        filename = self.config.script
        if os.name == "nt":
            # On Windows, one has to replace backslashes by slashes to avoid
            # confusion with escape characters (otherwise, for example, '\t'
            # will be interpreted as a tabulation):
            filename = os.path.normpath(filename).replace(os.sep, "/")
        self.p_args = ["-lvb", "-o", self.config.stats, filename]
        if self.config.args:
            self.p_args.extend(shlex.split(self.config.args))

        return self.process

    def start(self):
        self.process.start(
            self.config.kernprof,
            self.p_args,
            QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Unbuffered,
        )

        running = self.process.waitForStarted()
        if not running:
            self.output_error.emit(_("ERROR: Process failed to start"))

    @QtCore.Slot()
    def read_output(self):
        qbytearray = self.process.readAllStandardOutput()
        self.output_text.emit(LOCALE_CODEC.toUnicode(qbytearray))

    @QtCore.Slot()
    def read_error(self):
        qbytearray = self.process.readAllStandardError()
        self.output_error.emit(LOCALE_CODEC.toUnicode(qbytearray))

    @QtCore.Slot()
    def kill(self):
        if self.process is not None and self.process.state() == QtCore.QProcess.Running:
            self.process.kill()
            self.process.waitForFinished()
