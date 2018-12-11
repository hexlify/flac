import pickle
import struct
from mimetypes import guess_extension
from os.path import isdir, isfile, join
from typing import List, Tuple

from argparser import make_parser
from meta import BitStream, Flac
from player import PlayerApp, PlayerForm
from song import Song


def check_frame_blocks(actual, count):
    with open('../flac_dumps/frame{:06d}'.format(count), 'rb') as f:
        expected = pickle.load(f)
    assert actual == expected


def convert_to_wav(flac: Flac, wav_filename):
    with open(wav_filename, 'wb') as wav:
        wav.write(b'RIFF')
        byte_width = flac.sample_width // 8
        data_len = flac.total_samples * flac.channels * (byte_width)
        wav.write(struct.pack('<I', data_len + 36))
        wav.write(b'WAVE')
        wav.write(b'fmt ')
        wav.write(struct.pack(
            '<IHHIIHH', 16, 0x0001, flac.channels, flac.sample_rate,
            flac.sample_rate * flac.channels * (byte_width),
            flac.channels * (byte_width), flac.sample_width))
        wav.write(b'data')
        wav.write(struct.pack('<I', data_len))

        add_end = 128 if flac.sample_width == 8 else 0

        for frame_count, blocks in enumerate(flac.audio_data):
            progress = int(flac._f.tell() / flac.size * 100)
            print('{}%'.format(progress), end='\r')

            block_size = len(blocks[0])
            for i in range(block_size):
                for j in range(flac.channels):
                    wav.write(struct.pack(
                        '<i', blocks[j][i] + add_end)[:byte_width])


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

    if not isfile(args.file):
        print("Flac file doesn't exist")
        return

    flac = Flac(args.file)

    if args.command == 'play':
        Song(flac).play()

    if args.command == 'covers':
        extract_covers(flac, args.dir)

    if args.command == 'meta':
        meta_commands[args.type](flac)

    if args.command == 'conv':
        convert_to_wav(flac, args.wav_file)


if __name__ == '__main__':
    main()
