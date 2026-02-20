from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QGridLayout,
    QSlider,
    QSpinBox,
    QGroupBox,
)
from PySide6.QtCore import Qt, Signal
from collections import deque
import numpy as np

from core.tuner_engine import TunerEngine
from core.tone_generator import ToneGenerator
from utils.note_utils import frequency_to_note
from ui.tuner_meter import TunerMeter


NOTE_NAMES = [
    "C", "C#", "D", "D#", "E",
    "F", "F#", "G", "G#", "A", "A#", "B"
]


class TunerWidget(QWidget):

    pitch_detected = Signal(str, float, float)

    def __init__(self, audio_engine):
        super().__init__()

        self.audio_engine = audio_engine
        self.tuner = TunerEngine(buffer_size=2048)
        self.tone_generator = ToneGenerator(self.audio_engine)

        self.freq_buffer = deque(maxlen=5)

        self._setup_ui()
        self._setup_audio()

        self.pitch_detected.connect(self.update_ui)

    # ------------------------------------------------
    # UI
    # ------------------------------------------------

    def _setup_ui(self):
        main_layout = QVBoxLayout()

        self.note_label = QLabel("--")
        self.note_label.setAlignment(Qt.AlignCenter)
        self.note_label.setStyleSheet("font-size: 64px; font-weight: bold;")

        self.freq_label = QLabel("-- Hz")
        self.freq_label.setAlignment(Qt.AlignCenter)
        self.freq_label.setStyleSheet("font-size: 20px;")

        self.meter = TunerMeter()

        main_layout.addWidget(self.note_label)
        main_layout.addWidget(self.freq_label)
        main_layout.addWidget(self.meter)

        # Fork section
        fork_group = QGroupBox("Reference Tone")
        fork_layout = QVBoxLayout()

        grid = QGridLayout()
        self.note_buttons = {}

        for i, name in enumerate(NOTE_NAMES):
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name: self.select_note(n))
            self.note_buttons[name] = btn
            grid.addWidget(btn, i // 6, i % 6)

        fork_layout.addLayout(grid)

        # Octave
        octave_layout = QHBoxLayout()
        octave_layout.addWidget(QLabel("Octave:"))

        self.octave_spin = QSpinBox()
        self.octave_spin.setRange(1, 6)
        self.octave_spin.setValue(4)

        octave_layout.addWidget(self.octave_spin)
        fork_layout.addLayout(octave_layout)

        # Volume
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(30)
        self.volume_slider.valueChanged.connect(self.change_volume)

        volume_layout.addWidget(self.volume_slider)
        fork_layout.addLayout(volume_layout)

        # A4
        a4_layout = QHBoxLayout()
        a4_layout.addWidget(QLabel("A4:"))

        self.a4_spin = QSpinBox()
        self.a4_spin.setRange(400, 480)
        self.a4_spin.setValue(440)
        self.a4_spin.valueChanged.connect(self.change_a4)

        a4_layout.addWidget(self.a4_spin)
        fork_layout.addLayout(a4_layout)

        # Start/Stop tone
        self.tone_button = QPushButton("Start Tone")
        self.tone_button.clicked.connect(self.toggle_tone)

        fork_layout.addWidget(self.tone_button)

        fork_group.setLayout(fork_layout)
        main_layout.addWidget(fork_group)

        self.setLayout(main_layout)

    # ------------------------------------------------
    # Audio Input
    # ------------------------------------------------

    def _setup_audio(self):
        """
        Ensure microphone input stream is started safely.
        """

        # Avoid duplicate registration
        self.audio_engine.register_input_callback(self.audio_callback)

        # Start input only if not already running
        if self.audio_engine.input_stream is None:
            try:
                self.audio_engine.start_input_stream()
                print("Microphone stream started.")
            except Exception as e:
                print("Microphone start error:", e)

    # ------------------------------------------------
    # Audio Processing
    # ------------------------------------------------

    def audio_callback(self, block):
        freq = self.tuner.process(block)

        if freq:
            self.freq_buffer.append(freq)
            smooth_freq = np.median(self.freq_buffer)

            note, ref_freq, cents = frequency_to_note(
                smooth_freq,
                a4=self.a4_spin.value()
            )

            if note:
                self.pitch_detected.emit(note, smooth_freq, cents)

    # ------------------------------------------------
    # UI Update
    # ------------------------------------------------

    def update_ui(self, note, freq, cents):
        self.note_label.setText(note)
        self.freq_label.setText(f"{freq:.2f} Hz")
        self.meter.set_cents(cents)

    # ------------------------------------------------
    # Fork Controls
    # ------------------------------------------------

    def select_note(self, note_name):
        octave = self.octave_spin.value()
        self.tone_generator.set_note(note_name, octave)

    def change_volume(self, value):
        self.tone_generator.set_volume(value / 100)

    def change_a4(self, value):
        self.tone_generator.set_a4(value)

    def toggle_tone(self):
        if self.tone_generator.running:
            self.tone_generator.stop()
            self.tone_button.setText("Start Tone")
        else:
            self.tone_generator.start()
            self.tone_button.setText("Stop Tone")