import argparse


def make_parser():
    parser = argparse.ArgumentParser(description='Flac player')
    parser.add_argument('file', help='flac file')

    commands = parser.add_subparsers(title='commands', dest='command')
    commands.required = True

    meta = commands.add_parser('meta', help="show flac's metadata")
    meta_types = ['all', 'info', 'app', 'pic', 'tags']
    meta.add_argument('type', type=str, choices=meta_types,
                      help="metadata's type")

    play = commands.add_parser('play', help='play file')

    extract_covers = commands.add_parser('covers', help='extract covers')
    extract_covers.add_argument(
        'dir', default='.', help='directory path to extract covers to')

    convert = commands.add_parser('conv', help='convert flac to wav')
    convert.add_argument('wav_file', help='wav file')

    return parser
