import os
import shlex
import linecache

from qtpy import QtCore

from .utils import translate as _

LOCALE_CODEC = QtCore.QTextCodec.codecForLocale()


class KernprofRun(QtCore.QObject):
    output_text = QtCore.Signal(str)
    output_error = QtCore.Signal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config

        self.process = None
        self.p_args = None

    def prepare(self):
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(self.read_error)

        # Manage environment
        qenv = QtCore.QProcessEnvironment.systemEnvironment()
        for name, value in self.config.env.items():
            qenv.insert(name, value)
        self.process.setProcessEnvironment(qenv)

        self.process.setWorkingDirectory(self.config.wdir)
        filename = self.config.script
        warmup = self.config.warmup
        if os.name == "nt":
            # On Windows, one has to replace backslashes by slashes to avoid
            # confusion with escape characters (otherwise, for example, '\t'
            # will be interpreted as a tabulation):
            filename = os.path.normpath(filename).replace(os.sep, "/")
            if warmup:
                warmup = os.path.normpath(warmup).replace(os.sep, "/")
        self.p_args = ["-l", "-o", self.config.stats]
        if warmup:
            self.p_args.extend(["--setup", warmup])
        self.p_args.append(filename)
        if self.config.args:
            self.p_args.extend(shlex.split(self.config.args))

        return self.process

    def start(self):
        self.process.start(
            self.config.kernprof,
            self.p_args,
            QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Unbuffered,
        )

        # Check file cache now, to try to keep profiled files in the state that they were run
        linecache.checkcache()

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
