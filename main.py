import os
import pickle
import sys
from binascii import hexlify
from mimetypes import guess_extension
from os.path import isdir, isfile, join
from struct import pack
from time import sleep
from typing import Generator, List, Tuple

from npyscreen import blank_terminal

from flac.argparser import make_parser
from flac.meta import BitStream, Flac
from flac.player import PlayerApp
from flac.song import Song


def convert_to_wav(flac: Flac, wav_filename):
    with open(wav_filename, 'wb') as wav:
        wav.write(b'RIFF')
        byte_width = flac.sample_width // 8
        data_len = flac.total_samples * flac.channels * (byte_width)
        wav.write(pack('<I', data_len + 36))
        wav.write(b'WAVE')
        wav.write(b'fmt ')
        wav.write(pack(
            '<IHHIIHH', 16, 0x0001, flac.channels, flac.sample_rate,
            flac.sample_rate * flac.channels * (byte_width),
            flac.channels * (byte_width), flac.sample_width))
        wav.write(b'data')
        wav.write(pack('<I', data_len))

        for i, chunk in enumerate(flac.data):
            if i % 20 == 0:
                progress = int(flac._f.tell() / flac.size * 100)
                print('{}%'.format(progress), end='\r')
            wav.write(chunk)


def retrieve_data(flac: Flac):
    try:
        for chunk in flac.data:
            sys.stdout.write(hexlify(chunk).decode())
    except IOError:
        pass


def extract_covers(flac: Flac, path: str):
    if not isdir(path):
            print("Directory doesn't exist")
            return

    for i, pic in enumerate(flac.pictures):
        filename = join(path, str(i))
        ext = guess_extension(pic.mime_type)
        if ext is not None:
            filename += ext

        with open(filename, 'wb') as f:
            f.write(pic.image_data)


def print_all_meta(flac: Flac):
    print(str(flac._streaminfo) + '\n')
    for b in flac.metadata_blocks:
        print(str(b) + '\n')


def print_covers_info(flac: Flac):
    for b in flac.pictures:
        print(str(b) + '\n')


def print_application_info(flac: Flac):
    for b in flac.applications:
        print(str(b) + '\n')


def print_tags_info(flac: Flac):
    for b in flac.vorbis_comments:
        print(str(b) + '\n')


def print_streaminfo(flac: Flac):
    print(flac._streaminfo)


meta_commands = {
    'all': print_all_meta,
    'info': print_streaminfo,
    'app': print_application_info,
    'pic': print_covers_info,
    'tags': print_tags_info
}


def main():
    parser = make_parser()
    args = parser.parse_args()

    if not isfile(args.flac_file):
        print("Flac file doesn't exist")
        return

    flac = Flac(args.flac_file)

    if args.command == 'play':
        song = Song(flac)
        app = PlayerApp(song)
        sleep(3)
        os.system('clear')
        app.run()

    if args.command == 'covers':
        extract_covers(flac, args.dir)

    if args.command == 'meta':
        meta_commands[args.type](flac)

    if args.command == 'conv':
        convert_to_wav(flac, args.wav_file)

    if args.command == 'retr':
        retrieve_data(flac)


if __name__ == '__main__':
    main()
