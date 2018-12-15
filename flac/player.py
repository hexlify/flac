import curses
import sys

from npyscreen import (Form, FormBaseNew, NPSAppManaged, Pager, Slider,
                       TitleFixedText, TitleText, notify_wait)

from .meta import Flac
from .song import Song


class PlayerApp(NPSAppManaged):
    keypress_timeout_default = 1

    def __init__(self, song: Song):
        super().__init__()
        self.song = song

    def onStart(self):
        self.addForm('MAIN', PlayerForm)


class PlayerForm(FormBaseNew):
    SKIP_RATE = 5000
    VOLUME_RATE = 5
    HELP_MESSAGE = [
        'A == skip back',
        'D == skip forward',
        'W == turn volume up',
        'S == turn volume down',
        'SPACEBAR == pause/play',
        'R == stop',
        'Q == exit'
    ]

    def while_waiting(self):
        self.progress.value = self.song.current_time
        self.display()

    def create(self):
        self.song = self.parentApp.song  # type: Song
        self.add(TitleFixedText, name='Name: ', value=self.song.title or '???')
        self.add(TitleFixedText, name='Album: ',
                 value=self.song.album or '???')
        self.add(TitleFixedText, name='Artist: ',
                 value=self.song.artist or '???')
        # self.goto = self.add(Goto, name='Go to: ')
        self.progress = self.add(DurationSlider, out_of=self.song.duration)
        self.add(Pager, values=PlayerForm.HELP_MESSAGE)
        handlers = {
            ' ': self.h_pause,
            'w': self.h_turn_volume_up,
            's': self.h_turn_volume_down,
            'a': self.h_skip_back,
            'd': self.h_skip_forward,
            'r': self.h_stop,
            'q': self.h_quit}
        self.handlers = handlers

    def h_pause(self, _):
        if self.song.is_paused:
            self.song.play()
        else:
            self.song.pause()

    def h_turn_volume_up(self, _):
        self.song.change_volume(PlayerForm.VOLUME_RATE)

    def h_turn_volume_down(self, _):
        self.song.change_volume(-PlayerForm.VOLUME_RATE)

    def h_skip_forward(self, _):
        self.song.current_time += PlayerForm.SKIP_RATE

    def h_skip_back(self, _):
        self.song.current_time -= PlayerForm.SKIP_RATE

    def h_stop(self, _):
        self.song.stop()

    def h_quit(self, _):
        self.parentApp.switchForm(None)
        self.song.abort()
        sys.exit()


class DurationSlider(Slider):
    def translate_value(self):
        value = int(self.value) // 1000
        out_of = int(self.out_of) // 1000
        return '{:02d}:{:02d}/{:02d}:{:02d}'.format(
            value // 60, value % 60, out_of // 60, out_of % 60)


class Goto(TitleText):
    ...
