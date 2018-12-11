from binascii import hexlify

from ..bit_stream import BitStream
from .metadata import MetadataBlock


class Streaminfo(MetadataBlock):
    def __init__(self, size: int, is_last: bool, stream: BitStream):
        super().__init__(size, is_last)

        self.min_block_size = stream.read_uint(16)
        self.max_block_size = stream.read_uint(16)
        self.min_frame_size = stream.read_uint(24)
        self.max_frame_size = stream.read_uint(24)
        self.sample_rate = stream.read_uint(20)
        self.channels = stream.read_uint(3) + 1
        self.bits_per_sample = stream.read_uint(5) + 1
        self.total_samples = stream.read_uint(36)
        self.md5 = stream.read_bytes(16)

    def __str__(self):
        s = 'min_block_size: {}\n'.format(self.min_block_size)
        s += 'max_block_size: {}\n'.format(self.max_block_size)
        s += 'min_frame_size: {}\n'.format(self.min_frame_size)
        s += 'max_frame_size: {}\n'.format(self.max_frame_size)
        s += 'sample_rate: {}\n'.format(self.sample_rate)
        s += 'channels: {}\n'.format(self.channels)
        s += 'bits_per_sample: {}\n'.format(self.bits_per_sample)
        s += 'total_samples: {}\n'.format(self.total_samples)
        s += 'md5: {}'.format(hexlify(self.md5).decode())
        return s
