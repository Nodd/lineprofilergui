import textwrap

from qtpy.QtCore import Qt

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

        with qtbot.waitSignal(win.profile_finished, timeout=5000):
            win.actionRun.trigger()

    return win


class TestMainWindow:
    def test_profile_1_function(self, qtbot, tmp_path):
        code = """
        @profile
        def profiled_function():
            return "This was profiled"

        profiled_function()
        """
        win = run_code(code, tmp_path, qtbot)
        scriptfile = str(tmp_path / "script.py")

        lprof_path = tmp_path / "script.lprof"
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
        assert func_item.child(0).data(5, Qt.DisplayRole) == "def profiled_function():"
        assert (
            func_item.child(1).data(5, Qt.DisplayRole)
            == '    return "This was profiled"'
        )

        # Check file and line
        assert func_item.child(0).data(0, Qt.UserRole) == (scriptfile, 3)
        assert func_item.child(1).data(0, Qt.UserRole) == (scriptfile, 4)

    def test_profile_2_functions(self, qtbot, tmp_path):
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

        lprof_path = tmp_path / "script.lprof"
        assert lprof_path.is_file()
        assert (
            win.dockOutputWidget.outputWidget.toPlainText()
            == f"Wrote profile results to {lprof_path}\n"
        )

        tree = win.resultsTreeWidget
        assert tree.topLevelItemCount() == 2  # functions profiled

    def test_function_not_called(self, qtbot, tmp_path):
        code = """
        @profile
        def not_profiled_function():
            return "This was not profiled"
        """
        win = run_code(code, tmp_path, qtbot)

        lprof_path = tmp_path / "script.lprof"
        assert lprof_path.is_file()
        assert (
            win.dockOutputWidget.outputWidget.toPlainText()
            == f"Wrote profile results to {lprof_path}\n"
        )

        tree = win.resultsTreeWidget
        assert tree.topLevelItemCount() == 1  # function decorated but not profiled

    def test_warn_no_decorator(self, qtbot, tmp_path):
        code = """
        def not_profiled_function():
            return "This was not profiled"

        not_profiled_function()
        """
        win = run_code(code, tmp_path, qtbot)

        # No error
        lprof_path = tmp_path / "script.lprof"
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
