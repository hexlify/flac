from os.path import isfile
from typing import List, Tuple

from bitstruct import unpack

from .bit_stream import BitStream
from .blocks import *


FLAC_MARKER = b'fLaC'
block_types = {
    0: Streaminfo,
    2: Application,
    # 3: "SEEKTABLE",
    4: VorbisComment,
    # 5: "CUESHEET",
    6: Picture,
}


class Metadata:
    def __init__(self, filename: str):
        if not isfile(filename):
            raise FileExistsError("File doest exist")

        self._f = open(filename, 'rb')
        self._stream = BitStream(self._f)

        if self._stream.read_bytes(4) != FLAC_MARKER:
            raise ValueError('Bad flac file')

        blocks = self._parse_metadata_blocks()
        self._streaminfo = blocks[0]
        self._blocks = blocks[1:]

    def __del__(self):
        self._f.close()

    def _parse_metadata_blocks(self) -> List[MetadataBlock]:
        blocks = []
        while True:
            block = self._parse_metadata_block()
            blocks.append(block)
            if block.is_last:
                break

        return blocks

    def _parse_metadata_block(self) -> MetadataBlock:
        is_last = self._stream.read_uint(1)
        type = self._stream.read_uint(7)
        size = self._stream.read_uint(24)

        if type in block_types:
            return block_types[type](size, is_last == 1, self._stream)
        return Unknown(size, is_last == 1, self._stream)

    def get_all_data(self, all: bool) -> str:
        if not all:
            return str(self._streaminfo)

        res = str(self._streaminfo)
        for block in self._blocks:
            if isinstance(block, Unknown):
                continue
            res += '\n' + str(block)

        return res

    @property
    def sample_width(self):
        return self._streaminfo.bits_per_sample

    @property
    def frame_rate(self):
        return self._streaminfo.sample_rate

    @property
    def channels(self):
        return self._streaminfo.channels

    @property
    def pictures(self):
        return list(filter(lambda b: isinstance(b, Picture), self._blocks))
