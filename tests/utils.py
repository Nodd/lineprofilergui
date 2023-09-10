import os
import textwrap
from pathlib import Path

from lineprofilergui import main


def run_code(code: str, tmp_path: Path, qtbot):
    """Define helper function to run profiled code from UIMainWindow."""
    scriptfile = tmp_path / "script.py"
    scriptfile.write_text(textwrap.dedent(code))

    current_path = Path.cwd()
    try:
        os.chdir(tmp_path)

        main.icons_factory()
        win = main.UIMainWindow()
        qtbot.addWidget(win)

        win.config.script = str(scriptfile)

        with qtbot.waitSignal(win.profile_finished, timeout=10000):
            win.actionRun.trigger()
    finally:
        os.chdir(current_path)

    return win
