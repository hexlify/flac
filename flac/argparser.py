import argparse


def make_parser():
    parser = argparse.ArgumentParser(description='Flac player')
    parser.add_argument('file', help='flac file')

    commands = parser.add_subparsers(title='commands', dest='command')
    commands.required = True

    info = commands.add_parser('info', help='info about file')
    info.add_argument('--all', action='store_true', help='all info')

    play = commands.add_parser('play', help='play file')

    return parser