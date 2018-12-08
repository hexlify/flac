from typing import List, Tuple
from os.path import join, isdir
from mimetypes import guess_extension

from argparser import make_parser
from meta import Metadata
from song import Song


if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()

    # TODO сделай проверку на существование файла
    meta = Metadata(args.file)

    if args.command == 'info':
        print('\n' + meta.get_all_data(args.all))

    if args.command == 'play':
        song = Song(args.file)
        song.play()

    if args.command == 'covers':
        if not isdir(args.dir):
            raise FileNotFoundError('Directory does not exists')

        for i, pic in enumerate(meta.pictures):
            filename = join(args.dir, str(i))
            ext = guess_extension(pic.mime_type)
            if ext is not None:
                filename += ext

            with open(filename, 'wb') as f:
                f.write(pic.image_data)
