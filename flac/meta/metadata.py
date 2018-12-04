from typing import List, Tuple

from bitstruct import unpack

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
        with open(filename, 'rb') as f:
            self._data = f.read()
        if self._data[:4] != FLAC_MARKER:
            raise ValueError('Bad flac file')

        blocks = self._parse_metadata_blocks(4)
        self._streaminfo = blocks[0]
        self._blocks = blocks[1:]

    def _parse_metadata_blocks(self, start: int) -> List[MetadataBlock]:
        index = start
        blocks = []

        while True:
            block, index = self._parse_metadata_block(index)
            blocks.append(block)

            if block.is_last:
                break

        return blocks

    def _parse_metadata_block(self, start: int) -> Tuple[MetadataBlock, int]:
        is_last, type, size = unpack('>u1u7u24', self._data[start:start+4])
        start += 4
        if type in block_types:
            block = block_types[type](size, is_last == 1,
                                      self._data[start:start+size])
        else:
            block = Unknown(size, is_last == 1, b'')
        return (block, start + size)

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
