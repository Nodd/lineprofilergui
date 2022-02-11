import sys
import argparse

from qtpy import QtCore, QtWidgets

from .gui import UI_MainWindow
from .utils import icons_factory
from . import __version__


def positive_float(value):
    val = float(value)
    if val <= 0:
        raise argparse.ArgumentError
    return val


def commandline_args(args):
    """Manage arguments with argparse"""

    parser = argparse.ArgumentParser(
        description="Run, profile a python script and display results."
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s v{__version__}"
    )
    parser.add_argument(
        "-l", "--lprof", help="Display data from a .lprof file",
    )
    parser.add_argument(
        "-r", "--run", action="store_true", help="Profile the python script on launch"
    )
    parser.add_argument(
        "-o", "--outfile", help="Save stats to OUTFILE (default is a temporary file)",
    )
    parser.add_argument(
        "-s", "--setup", help="Python script to execute before the code to profile"
    )
    parser.add_argument("script", nargs="?", help="The python script file to run")
    parser.add_argument("args", nargs="...", help="Optional script arguments")

    if args is None:
        args = sys.argv[1:]
    options = parser.parse_args(args)

    options.args = " ".join(options.args)

    return options


def make_window(args=None):
    options = commandline_args(args)

    icons_factory()

    # Used for QSettings
    QtCore.QCoreApplication.setOrganizationName("OpenPyUtils")
    QtCore.QCoreApplication.setApplicationName("Line Profiler Gui")

    # Create main window
    win = UI_MainWindow()
    win.show()

    if options.lprof:
        win.load_lprof(options.lprof)

    win.config.script = options.script
    win.config.args = options.args
    win.config.warmup = options.setup
    win.config.outfile = options.outfile
    if options.script:
        win.update_window_title()
        if options.run:
            win.profile()
        else:
            win.configure()
    elif not options.lprof:
        win.configure()

    return win


def main():
    # Create Qt application
    app = QtWidgets.QApplication([])
    win = make_window()  # noqa: F841
    # Run Qt event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
