# from pytestqt import qtbot
from qtpy import QtCore, QtWidgets
from qtpy.QtCore import Qt

from lineprofilergui import main

SCRIPT = """
@profile
def profiled_function():
    return "This was profiled" + "0"

profiled_function()
"""


class TestMain:
    def test_profiling(self, qtbot, tmp_path):
        scriptfile = tmp_path / "script.py"
        scriptfile.write_text(SCRIPT)

        with tmp_path:
            main.icons_factory()
            win = main.UI_MainWindow()
            qtbot.addWidget(win)

            win.config.script = str(scriptfile)

            with qtbot.waitSignal(win.profile_finished, timeout=1000):
                win.actionRun.trigger()

        assert (tmp_path / "script.lprof").is_file()

        tree = win.resultsTreeWidget
        assert tree.topLevelItemCount() == 1  # functions profiled

        # Check function QTreeWidgetItem
        func_item = tree.topLevelItem(0)
        assert func_item.data(0, Qt.DisplayRole).startswith("profiled_function (")
        assert func_item.data(0, Qt.UserRole) == (str(scriptfile), "profiled_function")

        # Check number of lines
        assert func_item.childCount() == 2

        # Check line number
        for i in range(2):
            assert func_item.child(i).data(0, Qt.DisplayRole) == i + 3

        # Check hits
        assert func_item.child(0).data(1, Qt.DisplayRole) == ""
        assert func_item.child(1).data(1, Qt.DisplayRole) == "1"

        # Check %time
        assert func_item.child(0).data(4, Qt.DisplayRole) == ""
        assert func_item.child(1).data(4, Qt.DisplayRole) == "100.0"
