import textwrap

from lineprofilergui import main


def run_code(code, tmp_path, qtbot):
    """Helper function to run profiled code from UI_MainWindow"""
    scriptfile = tmp_path / "script.py"
    scriptfile.write_text(textwrap.dedent(code))

    with tmp_path:
        main.icons_factory()
        win = main.UI_MainWindow()
        qtbot.addWidget(win)

        win.config.script = str(scriptfile)

        with qtbot.waitSignal(win.profile_finished, timeout=10000):
            win.actionRun.trigger()

    return win
