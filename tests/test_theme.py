from lineprofilergui import main, theme


class TestTheme:
    # update_theme() is already run by the main window tests

    def test_dark_theme(self, qtbot):
        # Just check that the code runs without error
        win = main.UIMainWindow()
        qtbot.addWidget(win)
        theme.apply_dark_theme()

    def test_light_theme(self, qtbot):
        # Just check that the code runs without error
        win = main.UIMainWindow()
        qtbot.addWidget(win)
        theme.apply_default_theme()
