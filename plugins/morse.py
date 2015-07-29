# coding: utf-8

import math
import pyaudio
import random
import socket

from commands import Command


sample_rate = 44100
frequency = 1000.0
time_unit = 0.05
time_units = {
    'dit': time_unit,
    'dah': 3 * time_unit,
    'letter-pause': 3 * time_unit,
    'word-pause': 7 * time_unit,
    'fragment-pause': time_unit,
    'error': 5 * time_unit,
}


def standard_time_units(dit_time):
    return {
        'dit': dit_time,
        'dah': 3 * dit_time,
        'letter-pause': 3 * dit_time,
        'word-pause': 7 * dit_time,
        'fragment-pause': dit_time,
        'error': 5 * dit_time,
    }

def text_to_samples(text):
    morse = text_to_morse(text)
    notes = morse_to_notes(morse, time_units)
    return notes_to_samples(notes, frequency, sample_rate)


LETTER_TO_MORSE = {
    'A': '.-',
    'B': '-...',
    'C': '-.-.',
    'D': '-..',
    'E': '.',
    'F': '..-.',
    'G': '--.',
    'H': '....',
    'I': '..',
    'J': '.---',
    'K': '-.-',
    'L': '.-..',
    'M': '--',
    'N': '-.',
    'O': '---',
    'P': '.--.',
    'Q': '--.-',
    'R': '.-.',
    'S': '...',
    'T': '-',
    'U': '..-',
    'V': '...-',
    'W': '.--',
    'X': '-..-',
    'Y': '-.--',
    'Z': '--..',
    '0': '-----',
    '1': '.----',
    '2': '..---',
    '3': '...--',
    '4': '....-',
    '5': '.....',
    '6': '-....',
    '7': '--...',
    '8': '---..',
    '9': '----.',
}


def text_to_morse(text):
    morses = []
    words = text.split(" ")
    for word in words:
        morses.append(" ".join(LETTER_TO_MORSE.get(letter, '#') for letter in word.upper()))
    return "/".join(morses)


def morse_to_notes(morse, time_units):
    fragment_to_note = {
        '.': ('tone', time_units['dit']),
        '-': ('tone', time_units['dah']),
        ' ': ('pause', time_units['letter-pause'] - time_units['fragment-pause']),
        '/': ('pause', time_units['word-pause'] - time_units['fragment-pause']),
        '#': ('noise', time_units['error']),
    }
    notes = []
    for fragment in morse:
        notes += [fragment_to_note[fragment], ('pause', time_units['fragment-pause'])]
    return notes


def notes_to_samples(notes, frequency, sample_rate):
    data = ""
    period_samples = sample_rate / frequency
    sound_functions = {
        'tone': sine_wave,
        'pause': pause,
        'noise': noise,
    }
    for sound, time in notes:
        note_data = []
        total_samples = int(time * sample_rate)
        for i in range(total_samples):
            value = sound_functions[sound](i / period_samples)
            scale = envelope((time * i) / total_samples, time)
            note_data.append(to_sample(value * scale))
        data += "".join(note_data)
    return data


def envelope(time, duration):
    remaining = duration - time
    fade_duration = min(0.01, duration / 2)
    if time < fade_duration:
        return time / fade_duration
    elif remaining < fade_duration:
        return remaining / fade_duration
    else:
        return 1.0


def to_sample(value):
    signed = int(value * 127)
    if signed >= 0:
        return chr(signed)
    else:
        return chr(signed + 256)


def sine_wave(t):
    return math.sin(2 * math.pi * t)


def square_wave(t):
    if t - int(t) < 0.5:
        return -1
    else:
        return 1


def triangle_wave(t):
    t_prim = t - int(t)
    if t_prim < 0.5:
        return (4 * t_prim) - 1
    else:
        return (-4 * t_prim) + 3
    

def sawtooth_wave(t):
    return 2 * (t - int(t)) - 1

    
def noise(t):
    return random.uniform(-1, 1)


def pause(t):
    return 0


class MorsePlugin(Command):
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.s = self.p.open(format=pyaudio.paInt8, channels=1, rate=sample_rate, output=True)
        self.s.write(text_to_samples("OK"))

    def on_privmsg(self, bot, source, target, message):
        text = "<{}> {}".format(source.split("!")[0], message)
        self.s.write(text_to_samples(text))

if __name__ == '__main__':
    p = pyaudio.PyAudio()
    s = p.open(format=pyaudio.paInt8, channels=1, rate=sample_rate, output=True)
    s.write(text_to_samples("OK"))
    s.stop_stream()
    s.close()
    p.terminate()
