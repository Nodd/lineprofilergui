import sys
import argparse

from qtpy import QtWidgets

from .gui import UI_MainWindow
from .utils import _icons_factory
from . import __version__


def positive_float(value):
    val = float(value)
    if val <= 0:
        raise argparse.ArgumentError
    return val


def commandline_args():
    """Manage arguments with argparse"""

    parser = argparse.ArgumentParser(
        description="Run, profile a python script and display results."
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s v{__version__}"
    )
    parser.add_argument(
        "-r", "--run", action="store_true", help="Profile the python script on launch"
    )
    parser.add_argument(
        "-o", "--outfile", help="Save stats to OUTFILE (default: 'scriptname.lprof')"
    )

    # TODO
    # parser.add_argument(
    #     "-s", "--setup", help="Python script to execute before the code to profile"
    # )

    parser.add_argument("script", nargs="?", help="The python script file to run")
    parser.add_argument("args", nargs="...", help="Optional script arguments")

    options = parser.parse_args()

    options.args = " ".join(options.args)

    return options


def main():
    options = commandline_args()

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
            win.profile()
        else:
            win.configure()
    else:
        win.configure()

    # Run Qt event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
