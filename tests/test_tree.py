import subprocess

from qtpy import QtCore

from .utils import run_code


class TestResultsTreeWidget:
    """Specific checks for resultsTreeWidget behavior"""

    def test_collapse_expand(self, qtbot, tmp_path):
        """Check the tracking of expanded functions"""
        code = """
        @profile
        def profiled_function():
            return "This was profiled"

        profiled_function()
        """
        win = run_code(code, tmp_path, qtbot)
        scriptfile = str(tmp_path / "script.py")

        tree = win.resultsTreeWidget
        func_item = tree.topLevelItem(0)

        assert func_item.isExpanded()  # only 1 function, expanded
        assert tree.expanded_functions == {(scriptfile, "profiled_function")}

        func_item.setExpanded(False)
        assert tree.expanded_functions == set()

        func_item.setExpanded(True)
        assert tree.expanded_functions == {(scriptfile, "profiled_function")}

    def test_open_editor(self, qtbot, tmp_path, monkeypatch):
        """Check the command to open an editor at the correct line"""
        code = """
        @profile
        def profiled_function():
            return "This was profiled"

        profiled_function()
        """
        win = run_code(code, tmp_path, qtbot)

        # Monkeypatch QtCore.QSettings to give back the editor command
        class MockQSettings:
            def value(self, command, default):
                return "editor {file}:{line}"

            def beginGroup(self, group):
                pass

            def endGroup(self):
                pass

            def setValue(self, key, value):
                pass

        monkeypatch.setattr(QtCore, "QSettings", lambda: MockQSettings())

        # Monkeypatch subprocess.Popen
        popen_args = []
        monkeypatch.setattr(
            subprocess,
            "Popen",
            lambda command, shell: popen_args.append((command, shell)),
        )

        # "double-click" on a line
        tree = win.resultsTreeWidget
        func_item = tree.topLevelItem(0)
        line_item = func_item.child(0)
        tree.itemActivated.emit(line_item, 0)

        # Wait for subprocess.Popen call
        def wait_popen_call():
            assert popen_args

        qtbot.waitUntil(wait_popen_call)

        # Check that the editor command given to subprocess.Popen is correct
        scriptname_escaped = str(tmp_path / "script.py").replace("\\", "\\\\")
        assert popen_args == [(f'editor "{scriptname_escaped}":3', False)]
