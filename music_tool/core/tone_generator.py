NOTE_INDEX = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}


class ToneGenerator:
    def __init__(self, audio_engine, a4=440.0):
        self.audio_engine = audio_engine
        self.a4 = a4

        self.frequency = 440.0
        self.volume = 0.3
        self.running = False

    # -------------------------

    def set_a4(self, value):
        self.a4 = value

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))

        if self.running:
            self.audio_engine.enable_tone(
                self.frequency,
                self.volume
            )

    def set_note(self, note_name, octave):
        midi_number = (octave + 1) * 12 + NOTE_INDEX[note_name]
        self.frequency = self.a4 * (2 ** ((midi_number - 69) / 12))

        if self.running:
            self.audio_engine.enable_tone(
                self.frequency,
                self.volume
            )

    # -------------------------

    def start(self):
        if self.running:
            return

        self.running = True
        self.audio_engine.start_output_stream()
        self.audio_engine.enable_tone(
            self.frequency,
            self.volume
        )

    def stop(self):
        self.running = False
        self.audio_engine.disable_tone()