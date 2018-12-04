from typing import List, Tuple

from argparser import make_parser
from meta import Metadata
from song import Song


if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()

    if args.command == 'info':
        meta = Metadata(args.file)
        print('\n' + meta.get_all_data(args.all))

    if args.command == 'play':
        song = Song(args.file)
        # song.play()
