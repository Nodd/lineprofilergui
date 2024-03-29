from lineprofilergui.config import Config, UiConfigDialog
from lineprofilergui.utils import icons_factory


class TestConfig:
    def test_default_config(self, qtbot):
        icons_factory()
        config = Config()
        config_dialog = UiConfigDialog(None, config)

        assert not config.isvalid
        assert not config_dialog.profileButton.isEnabled()

    def test_config_with_script(self, qtbot):
        icons_factory()
        config = Config()
        config_dialog = UiConfigDialog(None, config)
        config_dialog.scriptWidget.setText(__file__)
        config_dialog.ui_to_config()

        assert config.isvalid
        assert config_dialog.profileButton.isEnabled()
