import sounddevice as sd
import numpy as np
import threading


class AudioEngine:
    def __init__(self, samplerate=44100, blocksize=2048):
        self.samplerate = samplerate
        self.blocksize = blocksize

        self.input_stream = None
        self.output_stream = None

        self.input_callback = None
        self._lock = threading.Lock()

        self._play_buffer = np.zeros(0, dtype="float32")

        self.tone_enabled = False
        self.tone_frequency = 440.0
        self.tone_volume = 0.3
        self._phase = 0.0

    # ------------------------------------------------
    # INPUT
    # ------------------------------------------------

    def register_input_callback(self, callback):
        self.input_callback = callback

    def _input_callback(self, indata, frames, time, status):
        if status:
            print("Input status:", status)

        if self.input_callback:
            audio_block = indata[:, 0].copy()
            self.input_callback(audio_block)

    def start_input_stream(self):
        if self.input_stream is None:
            self.input_stream = sd.InputStream(
                samplerate=self.samplerate,
                blocksize=self.blocksize,
                channels=1,
                dtype="float32",
                callback=self._input_callback,
            )
            self.input_stream.start()
            print("Input stream started.")

    def stop_input_stream(self):
        if self.input_stream:
            self.input_stream.stop()
            self.input_stream.close()
            self.input_stream = None

    # ------------------------------------------------
    # OUTPUT
    # ------------------------------------------------

    def _output_callback(self, outdata, frames, time, status):
        if status:
            print("Output status:", status)

        outdata.fill(0)

        with self._lock:
            # Tone
            if self.tone_enabled:
                t = np.arange(frames)
                wave = self.tone_volume * np.sin(
                    2 * np.pi * self.tone_frequency * t / self.samplerate
                    + self._phase
                )

                self._phase += (
                    2 * np.pi * self.tone_frequency * frames / self.samplerate
                )
                self._phase %= (2 * np.pi)

                outdata[:, 0] += wave.astype("float32")

            # Metronome
            if len(self._play_buffer) > 0:
                chunk = self._play_buffer[:frames]
                outdata[:len(chunk), 0] += chunk
                self._play_buffer = self._play_buffer[len(chunk):]

    def start_output_stream(self):
        if self.output_stream is None:
            self.output_stream = sd.OutputStream(
                samplerate=self.samplerate,
                blocksize=self.blocksize,
                channels=1,
                dtype="float32",
                callback=self._output_callback,
            )
            self.output_stream.start()

    def stop_output_stream(self):
        if self.output_stream:
            self.output_stream.stop()
            self.output_stream.close()
            self.output_stream = None

    # ------------------------------------------------

    def play_buffer(self, buffer):
        with self._lock:
            self._play_buffer = np.concatenate(
                (self._play_buffer, buffer.astype("float32"))
            )

    def enable_tone(self, frequency, volume):
        with self._lock:
            self.tone_frequency = frequency
            self.tone_volume = volume
            self.tone_enabled = True

    def disable_tone(self):
        with self._lock:
            self.tone_enabled = False