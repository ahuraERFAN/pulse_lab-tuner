from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QHBoxLayout,
    QSpinBox,
    QGroupBox,
    QComboBox,
    QCheckBox,
)
from PySide6.QtCore import Qt, QTimer, Signal
import time
from collections import deque

from core.metronome_engine import MetronomeEngine


class MetronomeWidget(QWidget):

    beat_signal = Signal(bool)
    tempo_signal = Signal(float)

    def __init__(self, audio_engine):
        super().__init__()

        self.audio_engine = audio_engine
        self.metronome = MetronomeEngine(self.audio_engine)

        self.tap_times = deque(maxlen=5)

        self._setup_ui()
        self._connect_signals()

        self.metronome.register_beat_callback(self._on_beat)
        self.metronome.register_tempo_callback(self._on_tempo)

        self.beat_signal.connect(self._flash)
        self.tempo_signal.connect(self._update_tempo_display)

    # ------------------------------------------------

    def _setup_ui(self):
        layout = QVBoxLayout()

        self.bpm_label = QLabel("BPM: 120")
        self.bpm_label.setAlignment(Qt.AlignCenter)
        self.bpm_label.setStyleSheet("font-size: 28px;")

        layout.addWidget(self.bpm_label)

        self.bpm_slider = QSlider(Qt.Horizontal)
        self.bpm_slider.setRange(20, 240)
        self.bpm_slider.setValue(120)
        layout.addWidget(self.bpm_slider)

        self.signature_combo = QComboBox()
        self.signature_combo.addItems([
            "1/1", "2/4", "3/4", "4/4",
            "5/4", "6/8", "7/8"
        ])
        layout.addWidget(self.signature_combo)

        practice_group = QGroupBox("Practice Mode")
        practice_layout = QVBoxLayout()

        self.practice_enable = QCheckBox("Enable Progressive Tempo")
        practice_layout.addWidget(self.practice_enable)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Start BPM:"))
        self.start_bpm_spin = QSpinBox()
        self.start_bpm_spin.setRange(20, 240)
        self.start_bpm_spin.setValue(60)
        row1.addWidget(self.start_bpm_spin)

        row1.addWidget(QLabel("End BPM:"))
        self.end_bpm_spin = QSpinBox()
        self.end_bpm_spin.setRange(20, 300)
        self.end_bpm_spin.setValue(120)
        row1.addWidget(self.end_bpm_spin)

        practice_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Duration (min):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 60)
        self.duration_spin.setValue(5)
        row2.addWidget(self.duration_spin)

        practice_layout.addLayout(row2)

        practice_group.setLayout(practice_layout)
        layout.addWidget(practice_group)

        self.start_button = QPushButton("Start")
        self.tap_button = QPushButton("Tap Tempo")

        layout.addWidget(self.start_button)
        layout.addWidget(self.tap_button)

        self.setLayout(layout)

    # ------------------------------------------------

    def _connect_signals(self):
        self.bpm_slider.valueChanged.connect(self.change_bpm)
        self.start_button.clicked.connect(self.toggle_metronome)
        self.tap_button.clicked.connect(self.tap_tempo)
        self.signature_combo.currentTextChanged.connect(self.change_signature)

    # ------------------------------------------------

    def change_bpm(self, value):
        self.bpm_label.setText(f"BPM: {value}")
        self.metronome.set_bpm(value)

    def change_signature(self, text):
        beats, note = text.split("/")
        self.metronome.set_time_signature(int(beats), int(note))

    def toggle_metronome(self):
        if self.metronome.running:
            self.metronome.stop()
            self.start_button.setText("Start")
            return

        if self.practice_enable.isChecked():
            start = self.start_bpm_spin.value()
            end = self.end_bpm_spin.value()
            duration = self.duration_spin.value() * 60
            self.metronome.enable_practice_mode(start, end, duration)
        else:
            self.metronome.disable_practice_mode()

        self.metronome.start()
        self.start_button.setText("Stop")

    # ------------------------------------------------

    def tap_tempo(self):
        now = time.time()

        if self.tap_times and now - self.tap_times[-1] > 2:
            self.tap_times.clear()

        self.tap_times.append(now)

        if len(self.tap_times) < 2:
            return

        intervals = [
            self.tap_times[i] - self.tap_times[i - 1]
            for i in range(1, len(self.tap_times))
        ]

        avg_interval = sum(intervals) / len(intervals)
        bpm = int(60 / avg_interval)
        bpm = max(20, min(240, bpm))

        self.bpm_slider.setValue(bpm)
        self.metronome.set_bpm(bpm)

    # ------------------------------------------------

    def _on_beat(self, is_accent):
        self.beat_signal.emit(is_accent)

    def _on_tempo(self, bpm):
        self.tempo_signal.emit(bpm)

    def _update_tempo_display(self, bpm):
        self.bpm_label.setText(f"BPM: {int(bpm)}")

    def _flash(self, is_accent):
        color = "#00ffaa" if is_accent else "#4444ff"

        self.start_button.setStyleSheet(
            f"background-color: {color}; border-radius: 8px;"
        )

        QTimer.singleShot(80, self._reset_flash)

    def _reset_flash(self):
        self.start_button.setStyleSheet("")