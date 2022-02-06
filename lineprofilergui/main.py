import sys
import argparse

from .gui import create_app
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
    app = create_app(options)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
