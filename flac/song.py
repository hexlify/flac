from typing import TextIO

from pyaudio import PyAudio, paInt16, paInt32
from pydub import AudioSegment
from pydub.utils import make_chunks

from meta import Metadata


class Song:
    def __init__(self, filename: str):
        self.meta = Metadata(filename)
        self._segment = AudioSegment.from_file(filename)
        self._audio = PyAudio()
        self._stream = self._open_stream()
        self._is_paused = True

    def _open_stream(self):
        if self.meta.sample_width not in [16, 24]:
            raise ValueError('This frame width are not supported')

        format = paInt16 if self.meta.sample_width == 16 else paInt32

        return self._audio.open(
            format=format, channels=self.meta.channels,
            rate=self.meta.frame_rate, output=True)

    def pause(self):
        self._is_paused = True

    def play(self):
        self._is_paused = False

    def run(self):
        chunk_count = 0
        chunks = make_chunks(self._segment, 100)
        while chunk_count <= len(chunks):
            if not self._is_paused:
                data = chunks[chunk_count]._data
                chunk_count += 1
            else:
                free = self._stream.get_write_available()
                data = chr(0) * free
            self._stream.write(data)

        self._stream.stop_stream()
        self._audio.terminate()
