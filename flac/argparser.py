import argparse


def make_parser():
    parser = argparse.ArgumentParser(description='Flac player')
    parser.add_argument('file', help='flac file')

    commands = parser.add_subparsers(title='commands', dest='command')
    commands.required = True

    info = commands.add_parser('info', help='info about file')
    info.add_argument('--all', action='store_true', help='all info')

    play = commands.add_parser('play', help='play file')

    extract_covers = commands.add_parser('covers', help='extract covers')
    extract_covers.add_argument(
        'dir', default='.', help='directory path to extract covers to')

    return parser
