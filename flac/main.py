from typing import List, Tuple

from bitstruct import unpack

from argparser import make_parser
from blocks import *

FLAC_MARKER = b'fLaC'

block_types = {
    0: Streaminfo,
    # 1: "PADDING",
    # 2: "APPLICATION",
    # 3: "SEEKTABLE",
    4: VorbisComment,
    # 5: "CUESHEET",
    6: Picture,
}


def parse_metadata_blocks(data: bytes, start: int) -> List[MetadataBlock]:
    index = start
    blocks = []

    while True:
        block, index = parse_metadata_block(data, index)
        blocks.append(block)

        if block.is_last:
            break

    return blocks


def parse_metadata_block(data: bytes, start: int) -> Tuple[MetadataBlock, int]:
    is_last, type, size = unpack('>u1u7u24', data[start:start+4])
    start += 4
    if type in block_types:
        block = block_types[type](size, is_last == 1, data[start:start+size])
    else:
        block = Unknown(size, is_last == 1, b'')
    return (block, start + size)


def print_info(data: bytes):
    marker = data[:4]
    if marker != FLAC_MARKER:
        print('Bad flac file')
        return

    blocks = parse_metadata_blocks(data, 4)
    for block in filter(lambda b: not isinstance(b, Unknown), blocks):
        print(block)


if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()

    with open(args.file, 'rb') as f:
        flac_data = f.read()

    if args.command == 'info':
        print_info(flac_data)
