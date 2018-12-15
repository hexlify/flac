from threading import Thread
from typing import Optional, TextIO

from pyaudio import PyAudio, paInt16, paInt32
from pydub import AudioSegment

from .meta import Flac

CHUNK_DURATION = 50


class Song(Thread):
    def __init__(self, flac: Flac):
        self._flac = flac
        self._segment = AudioSegment.from_file(flac._f)
        self._audio = PyAudio()
        self._stream = self._open_stream()
        self._is_paused = True
        self._current_time = 0
        self.is_aborted = False

        Thread.__init__(self)
        self.start()

    def _open_stream(self):
        if self._flac.sample_width not in [16, 24]:
            raise ValueError("This sample width isn't supported")

        format = paInt16 if self._flac.sample_width == 16 else paInt32
        return self._audio.open(
            format=format, channels=self._flac.channels,
            rate=self._flac.sample_rate, output=True)

    @property
    def is_paused(self):
        return self._is_paused

    def pause(self):
        self._is_paused = True

    def play(self):
        self._is_paused = False

    def stop(self):
        self._current_time = 0

    def abort(self):
        self.is_aborted = True

    @property
    def duration(self):
        return len(self._segment)

    @property
    def current_time(self):
        return self._current_time

    @current_time.setter
    def current_time(self, milliseconds: int):
        if milliseconds < 0:
            milliseconds = 0
        if milliseconds >= len(self._segment):
            milliseconds = len(self._segment) - 1

        self._current_time = milliseconds

    def change_volume(self, volume_change: int):
        self._segment += volume_change

    def _get_tag(self, tag: str) -> Optional[str]:
        comments = self._flac.vorbis_comments
        if len(comments) == 0:
            return None
        return comments[0].tags.get(tag, [None])[0]

    @property
    def title(self) -> Optional[str]:
        return self._get_tag('TITLE')

    @property
    def album(self) -> Optional[str]:
        return self._get_tag('ALBUM')

    @property
    def artist(self) -> Optional[str]:
        return self._get_tag('ARTIST')

    def run(self):
        while self._current_time <= len(self._segment) and not self.is_aborted:
            if not self._is_paused:
                data = self._segment[
                    self._current_time:self._current_time+CHUNK_DURATION]._data
                self._current_time += CHUNK_DURATION
            else:
                free = self._stream.get_write_available()
                data = chr(0) * free
            self._stream.write(data)

        self._stream.stop_stream()
        self._audio.terminate()
