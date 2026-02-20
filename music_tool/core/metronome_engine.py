import numpy as np
import threading
import time


class MetronomeEngine:
    def __init__(self, audio_engine):
        self.audio_engine = audio_engine

        self.bpm = 120
        self.start_bpm = 120
        self.end_bpm = 120
        self.practice_duration = 0
        self.practice_mode = False

        self.beats_per_bar = 4
        self.note_value = 4

        self.running = False
        self._thread = None

        self.sample_rate = self.audio_engine.samplerate

        self.beat_callback = None
        self.tempo_callback = None

        self.accent_click = self._generate_click(1600)
        self.normal_click = self._generate_click(1000)

    # -------------------------

    def _generate_click(self, freq, duration=0.05):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        click = 0.6 * np.sin(2 * np.pi * freq * t)

        fade_len = int(0.01 * self.sample_rate)
        fade = np.linspace(1, 0, fade_len)
        click[-fade_len:] *= fade

        return click.astype("float32")

    # -------------------------

    def set_bpm(self, bpm):
        self.bpm = max(1, bpm)

    def set_time_signature(self, beats, note_value):
        self.beats_per_bar = max(1, beats)
        self.note_value = max(1, note_value)

    def enable_practice_mode(self, start_bpm, end_bpm, duration_seconds):
        self.start_bpm = start_bpm
        self.end_bpm = end_bpm
        self.practice_duration = max(1, duration_seconds)
        self.practice_mode = True

    def disable_practice_mode(self):
        self.practice_mode = False

    def register_beat_callback(self, callback):
        self.beat_callback = callback

    def register_tempo_callback(self, callback):
        self.tempo_callback = callback

    # -------------------------

    def start(self):
        if self.running:
            return

        self.running = True
        self.audio_engine.start_output_stream()

        self._thread = threading.Thread(
            target=self._run,
            daemon=True
        )
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join()
            self._thread = None

    # -------------------------

    def _run(self):
        next_time = time.perf_counter()
        beat_index = 0
        practice_start_time = time.perf_counter()

        while self.running:
            now = time.perf_counter()

            if self.practice_mode:
                elapsed = now - practice_start_time
                progress = min(1.0, elapsed / self.practice_duration)
                self.bpm = self.start_bpm + progress * (
                    self.end_bpm - self.start_bpm
                )

            interval = 60.0 / self.bpm

            if now >= next_time:
                is_primary = (beat_index % self.beats_per_bar) == 0

                if is_primary:
                    self.audio_engine.play_buffer(self.accent_click)
                else:
                    self.audio_engine.play_buffer(self.normal_click)

                if self.beat_callback:
                    self.beat_callback(is_primary)

                if self.tempo_callback:
                    self.tempo_callback(self.bpm)

                beat_index += 1
                next_time += interval

            time.sleep(0.0005)