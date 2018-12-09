import struct
from mimetypes import guess_extension
from os.path import isdir, join
from typing import List, Tuple

from argparser import make_parser
from meta import BitStream, Flac
from song import Song


def convert_to_wav(flac: Flac, wav_filename):
    with open(wav_filename, 'wb') as wav:
        wav.write(b'RIFF')
        data_len = flac.total_samples * flac.channels * (flac.sample_width // 8)
        wav.write(struct.pack('<I', data_len + 36))
        wav.write(b'WAVE')
        wav.write(b'fmt')
        wav.write(struct.pack(
            '<IHHIIHH', 16, 0x0001, flac.channels, flac.sample_rate,
            flac.sample_rate * flac.channels * (flac.sample_width // 8),
            flac.channels * (flac.sample_width // 8), flac.sample_width))
        wav.write(b'data')
        wav.write(struct.pack('<I', data_len))

        add_end = 128 if flac.sample_width == 8 else 0

        for i, blocks in enumerate(flac.read_audio_data()):
            if (i + 1) % 10 == 0:
                print(i + 1)
            block_size = len(blocks[0])
            for i in range(block_size):
                for j in range(flac.channels):
                    wav.write(struct.pack(
                        '<i', blocks[j][i] + add_end)[:flac.sample_width // 8])


if __name__ == '__main__':
    f = Flac('../sample16.flac')
    convert_to_wav(f, '/tmp/my.wav')


# if __name__ == '__main__':
#     parser = make_parser()
#     args = parser.parse_args()

#     # TODO сделай проверку на существование файла
#     meta = Metadata(args.file)

#     if args.command == 'info':
#         print('\n' + meta.get_all_data(args.all))

#     if args.command == 'play':
#         song = Song(args.file)
#         song.play()

#     if args.command == 'covers':
#         if not isdir(args.dir):
#             raise FileNotFoundError('Directory does not exists')

#         for i, pic in enumerate(meta.pictures):
#             filename = join(args.dir, str(i))
#             ext = guess_extension(pic.mime_type)
#             if ext is not None:
#                 filename += ext

#             with open(filename, 'wb') as f:
#                 f.write(pic.image_data)
