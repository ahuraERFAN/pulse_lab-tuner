import numpy as np

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F",
              "F#", "G", "G#", "A", "A#", "B"]


def frequency_to_midi(frequency, a4=440.0):
    if frequency <= 0:
        return None
    return 69 + 12 * np.log2(frequency / a4)


def midi_to_frequency(midi_note, a4=440.0):
    return a4 * (2 ** ((midi_note - 69) / 12))


def midi_to_note_name(midi_note):
    note_index = int(midi_note) % 12
    octave = int(midi_note) // 12 - 1
    return f"{NOTE_NAMES[note_index]}{octave}"


def cents_difference(frequency, reference_frequency):
    return 1200 * np.log2(frequency / reference_frequency)


def frequency_to_note(frequency, a4=440.0):
    """
    Returns:
        note_name (str)
        nearest_frequency (float)
        cents (float)
    """
    if frequency is None or frequency <= 0:
        return None, None, None

    midi = frequency_to_midi(frequency, a4)
    nearest_midi = int(round(midi))

    nearest_freq = midi_to_frequency(nearest_midi, a4)
    cents = cents_difference(frequency, nearest_freq)

    note_name = midi_to_note_name(nearest_midi)

    return note_name, nearest_freq, cents