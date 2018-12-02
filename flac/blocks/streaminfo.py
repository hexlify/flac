import struct as byte
import bitstruct as bit


from .metadata import MetadataBlock


class Streaminfo(MetadataBlock):
    def __init__(self, length: int, is_last: bool, data: bytes):
        if len(data) != length or length < 0:
            raise ValueError()

        super().__init__(length, is_last)
        self.min_block_size, self.max_block_size = byte.unpack('>HH', data[:4])
        self.min_frame_size = byte.unpack('>I', b'\x00' + data[4:7])[0]
        self.max_frame_size = byte.unpack('>I', b'\x00' + data[7:10])[0]
        (self.sample_rate, self.channels, self.bits_per_sample,
         self.total_samples) = bit.unpack('>u20u3u5u36', data[10:18])
        self.md5 = data[18:]
