from threading import Thread
from typing import TextIO

from pyaudio import PyAudio, paInt16, paInt32
from pydub import AudioSegment

from meta import Flac


CHUNK_DURATION = 50


class Song(Thread):
    def __init__(self, flac: Flac):
        self._flac = flac
        self._segment = AudioSegment.from_file(flac._f)
        self._audio = PyAudio()
        self._is_paused = True
        self._current_time = 0

        Thread.__init__(self)
        self.start()

    def _open_stream(self):
        if self._flac.sample_width not in [16, 24]:
            raise ValueError("This sample width isn't supported")

        format = paInt16 if self._flac.sample_width == 16 else paInt32
        return self._audio.open(
            format=format, channels=self._flac.channels,
            rate=self._flac.sample_rate, output=True)

    def pause(self):
        self._is_paused = True

    def play(self):
        self._is_paused = False

    def stop(self):
        self._current_time = 0

    @property
    def name(self):
        return self._flac._f.name

    @property
    def duration(self):
        return len(self._segment) // 10000

    @property
    def current_time(self):
        return self._current_time // 1000

    def go_to(self, seconds):
        if not (0 <= seconds <= len(self._segment) // 1000):
            raise ValueError("Seconds can't be negative either greater "
                             "than song's duration")
        self._current_time = 1000 * seconds

    def set_volume(self, volume):
        # TODO: validate
        ...

    def run(self):
        stream = self._open_stream()

        while self._current_time <= len(self._segment):
            if not self._is_paused:
                data = self._segment[
                    self._current_time:self._current_time+CHUNK_DURATION]._data
                self._current_time += CHUNK_DURATION
            else:
                free = stream.get_write_available()
                data = chr(0) * free
            stream.write(data)

        stream.stop_stream()
        self._audio.terminate()
