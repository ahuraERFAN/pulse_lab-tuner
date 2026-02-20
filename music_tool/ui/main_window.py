from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QMessageBox,
    QMenuBar,
)
from core.audio_engine import AudioEngine
from ui.tuner_widget import TunerWidget
from ui.metronome_widget import MetronomeWidget
from utils.settings_manager import SettingsManager
from version import APP_NAME, APP_VERSION, APP_AUTHOR


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings = SettingsManager()
        self.audio_engine = AudioEngine()

        self._setup_ui()
        self._setup_menu()
        self._load_settings()

    # -------------------------

    def _setup_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.tabs = QTabWidget()

        self.tuner_tab = TunerWidget(self.audio_engine)
        self.metronome_tab = MetronomeWidget(self.audio_engine)

        self.tabs.addTab(self.tuner_tab, "🎸 Tuner")
        self.tabs.addTab(self.metronome_tab, "🎵 Metronome")

        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

    # -------------------------

    def _setup_menu(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        help_menu = menu_bar.addMenu("Help")

        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self._show_about)

    # -------------------------

    def _show_about(self):
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"""
<b>{APP_NAME}</b><br>
Version: {APP_VERSION}<br>
Author: {APP_AUTHOR}<br><br>
Professional Tuner & Metronome<br>
with Progressive Practice Mode
"""
        )

    # -------------------------

    def _load_settings(self):
        a4 = self.settings.get("a4", 440)
        volume = self.settings.get("fork_volume", 30)
        bpm = self.settings.get("bpm", 120)
        signature = self.settings.get("signature", "4/4")

        self.tuner_tab.a4_spin.setValue(a4)
        self.tuner_tab.volume_slider.setValue(volume)

        self.metronome_tab.bpm_slider.setValue(bpm)

        index = self.metronome_tab.signature_combo.findText(signature)
        if index >= 0:
            self.metronome_tab.signature_combo.setCurrentIndex(index)

    # -------------------------

    def _save_settings(self):
        self.settings.set("a4", self.tuner_tab.a4_spin.value())
        self.settings.set("fork_volume", self.tuner_tab.volume_slider.value())
        self.settings.set("bpm", self.metronome_tab.bpm_slider.value())
        self.settings.set("signature", self.metronome_tab.signature_combo.currentText())
        self.settings.save()

    # -------------------------

    def closeEvent(self, event):
        if self.metronome_tab.metronome.running:
            self.metronome_tab.metronome.stop()

        if self.tuner_tab.tone_generator.running:
            self.tuner_tab.tone_generator.stop()

        self.audio_engine.stop_input_stream()
        self.audio_engine.stop_output_stream()

        self._save_settings()

        event.accept()