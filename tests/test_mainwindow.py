import textwrap
from pathlib import Path
import xml

from qtpy.QtCore import Qt

from lineprofilergui import main

from .utils import run_code


class TestMainWindow:
    """Global checks for the main window and profiling results

    Those are more functional tests rather than unit tests,
    but at least is assures that there is no basic problem in most of the code.
    """

    def test_profile_1_function(self, qtbot, tmp_path):
        """Check that the result tree is filled correctly"""
        code = """
        @profile
        def profiled_function():
            return "This was profiled"

        profiled_function()
        """
        win = run_code(code, tmp_path, qtbot)
        scriptfile = str(tmp_path / "script.py")

        lprof_path = Path(win.config.stats)
        assert lprof_path.is_file()
        assert (
            win.dockOutputWidget.outputWidget.toPlainText()
            == f"Wrote profile results to {lprof_path}\n"
        )

        tree = win.resultsTreeWidget
        assert tree.topLevelItemCount() == 1  # functions profiled

        # Check function QTreeWidgetItem
        func_item = tree.topLevelItem(0)
        assert func_item.data(0, Qt.DisplayRole).startswith("profiled_function (")
        assert func_item.data(0, Qt.UserRole) == (scriptfile, "profiled_function")

        # Check number of lines
        assert func_item.childCount() == 2

        # Check line number
        assert func_item.child(0).data(0, Qt.DisplayRole) == 3
        assert func_item.child(1).data(0, Qt.DisplayRole) == 4

        # Check hits
        assert func_item.child(0).data(1, Qt.DisplayRole) == ""
        assert func_item.child(1).data(1, Qt.DisplayRole) == "1"

        # Check %time
        assert func_item.child(0).data(4, Qt.DisplayRole) == ""
        assert func_item.child(1).data(4, Qt.DisplayRole) == "100.0"

        # Check code
        def remove_tags(text):
            return "".join(xml.etree.ElementTree.fromstring(text).itertext()).rstrip()

        assert (
            remove_tags(tree.itemWidget(func_item.child(0), 5).text())
            == "def profiled_function():"
        )
        assert (
            remove_tags(tree.itemWidget(func_item.child(1), 5).text())
            == '    return "This was profiled"'
        )

        # Check file and line
        assert func_item.child(0).data(0, Qt.UserRole) == (scriptfile, 3)
        assert func_item.child(1).data(0, Qt.UserRole) == (scriptfile, 4)

    def test_profile_2_functions(self, qtbot, tmp_path):
        """Check the profiling of 2 different functions"""
        code = """
        @profile
        def profiled_function1():
            return "This was profiled"

        @profile
        def profiled_function2():
            return "This was profiled too"

        profiled_function1()
        profiled_function2()
        """
        win = run_code(code, tmp_path, qtbot)

        lprof_path = Path(win.config.stats)
        assert lprof_path.is_file()
        assert (
            win.dockOutputWidget.outputWidget.toPlainText()
            == f"Wrote profile results to {lprof_path}\n"
        )

        tree = win.resultsTreeWidget
        assert tree.topLevelItemCount() == 2  # functions profiled

    def test_function_not_called(self, qtbot, tmp_path):
        """Check the case of a decoracted function not called"""
        code = """
        @profile
        def not_profiled_function():
            return "This was not profiled"
        """
        win = run_code(code, tmp_path, qtbot)

        lprof_path = Path(win.config.stats)
        assert lprof_path.is_file()
        assert (
            win.dockOutputWidget.outputWidget.toPlainText()
            == f"Wrote profile results to {lprof_path}\n"
        )

        tree = win.resultsTreeWidget
        assert tree.topLevelItemCount() == 1  # function decorated but not profiled

    def test_warn_no_decorator(self, qtbot, tmp_path):
        """Check the case of no @profile decorator in script"""
        code = """
        def not_profiled_function():
            return "This was not profiled"

        not_profiled_function()
        """
        win = run_code(code, tmp_path, qtbot)

        # No error
        lprof_path = Path(win.config.stats)
        assert lprof_path.is_file()
        assert (
            win.dockOutputWidget.outputWidget.toPlainText()
            == f"Wrote profile results to {lprof_path}\n"
        )

        tree = win.resultsTreeWidget
        assert tree.topLevelItemCount() == 1  # Warning

        warn_item = tree.topLevelItem(0)
        assert (
            warn_item.data(0, Qt.DisplayRole)
            == "No timings to display. Did you forget to add @profile decorators ?"
        )
        assert warn_item.data(0, Qt.UserRole) is None

    def test_script_error(self, qtbot, tmp_path):
        """Check the case of the script ending with an error"""
        code = "1 / 0"
        win = run_code(code, tmp_path, qtbot)

        log = win.dockOutputWidget.outputWidget.toPlainText()
        lines = log.split("\n")
        assert lines[-1] == "ZeroDivisionError: division by zero"

    def test_script_kill(self, qtbot, tmp_path):
        """Check the case of a script killed"""
        code = """
        import time
        def long_running_function():
            time.sleep(20)

        long_running_function()
        """
        scriptfile = tmp_path / "script.py"
        scriptfile.write_text(textwrap.dedent(code))

        with tmp_path:
            main.icons_factory()
            win = main.UI_MainWindow()
            qtbot.addWidget(win)

            win.config.script = str(scriptfile)

            with qtbot.waitSignal(win.profile_finished, timeout=10000):
                win.actionRun.trigger()
                win.actionAbort.trigger()

        tree = win.resultsTreeWidget
        assert tree.topLevelItemCount() == 1  # Warning

        warn_item = tree.topLevelItem(0)
        assert warn_item.data(0, Qt.DisplayRole) == "No profiling results"
        assert warn_item.data(0, Qt.UserRole) is None

    def test_load_lprof(self, qtbot, tmp_path):
        """Check that laoding a .lprof file directly works"""
        code = """
        @profile
        def profiled_function():
            return "This was profiled"

        profiled_function()
        """
        win = run_code(code, tmp_path, qtbot)
        lprof_path = Path(win.config.stats)
        assert lprof_path.is_file()

        win.load_lprof(str(lprof_path))
        assert win.historyCombo.count() == 2  # Initial profiling + lprof load
