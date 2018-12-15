import struct
from os.path import getsize
from typing import Generator, List, Tuple

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

FIXED_SUBFRAME_COEFFS = [
    [],
    [1],
    [2, -1],
    [3, -3, 1],
    [4, -6, 4, 1],
]  # type: List[List[int]]


class Flac:
    def __init__(self, filename: str):
        self._f = open(filename, 'rb')
        self.size = getsize(filename)
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

    @property
    def sample_width(self):
        return self._streaminfo.bits_per_sample

    @property
    def sample_rate(self):
        return self._streaminfo.sample_rate

    @property
    def channels(self):
        return self._streaminfo.channels

    @property
    def total_samples(self):
        return self._streaminfo.total_samples

    @property
    def metadata_blocks(self):
        blocks = [self._streaminfo]
        blocks.extend(self._blocks)
        return list(filter(lambda b: not isinstance(b, Unknown), blocks))

    @property
    def pictures(self):
        return list(filter(lambda b: isinstance(b, Picture), self._blocks))

    @property
    def vorbis_comments(self):
        return list(filter(lambda b: isinstance(b, VorbisComment),
                           self._blocks))

    @property
    def applications(self):
        return list(filter(lambda b: isinstance(b, Application), self._blocks))

    @property
    def data(self) -> Generator[bytes, None, None]:
        added_val = 128 if self.sample_width == 8 else 0
        sample_width = self.sample_width // 8

        for blocks in self._audio_data:
            block_size = len(blocks[0])
            for i in range(block_size):
                for j in range(self.channels):
                    yield struct.pack(
                        '<i', blocks[j][i] + added_val)[:sample_width]

    @property
    def _audio_data(self) -> Generator[List[List[int]], None, None]:
        try:
            while True:
                yield self._decode_frame(self.sample_width)
        except EOFError:
            pass

    def _decode_frame(self, bits_per_sample: int) -> List[List[int]]:
        sync_code = self._stream.read_uint(14)
        if sync_code != 0b11111111111110:
            raise ValueError('Invalid sync code')

        self._stream.read_uint(1)  # reserved bit
        self._stream.read_uint(1)  # block strategy
        block_size_code = self._stream.read_uint(4)
        sample_rate_code = self._stream.read_uint(4)
        channel_assigment = self._stream.read_uint(4)
        self._stream.read_uint(3)  # sample size
        self._stream.read_uint(1)  # reserved bit

        temp = self._stream.read_uint(8)
        while temp >= 0b11000000:
            self._stream.read_uint(8)
            temp = (temp << 1) & 0xFF

        if block_size_code == 1:
            block_size = 192
        elif 2 <= block_size_code <= 5:
            block_size = 576 << (block_size_code - 2)
        elif block_size_code == 6:
            block_size = self._stream.read_uint(8) + 1
        elif block_size_code == 7:
            block_size = self._stream.read_uint(16) + 1
        elif 8 <= block_size_code <= 15:
            block_size = 256 << (block_size_code - 8)

        if sample_rate_code == 12:
            self._stream.read_uint(8)
        elif sample_rate_code in [13, 14]:
            self._stream.read_uint(16)

        self._stream.read_uint(8)  # crc-8

        blocks = self._decode_subframes(block_size, bits_per_sample,
                                        channel_assigment)
        self._stream._clear_buffer()  # align to byte
        self._stream.read_uint(16)  # crc-16

        return blocks

    def _decode_subframes(self, block_size: int, bits_per_sample: int,
                          channel_assigment: int) -> List[List[int]]:
        if 0 <= channel_assigment <= 7:
            return [self._decode_subframe(block_size, bits_per_sample)
                    for _ in range(channel_assigment + 1)]

        if channel_assigment == 8:
            left = self._decode_subframe(block_size, bits_per_sample)
            diff = self._decode_subframe(block_size, bits_per_sample + 1)
            for i in range(block_size):
                diff[i] = left[i] - diff[i]
            return [left, diff]

        if channel_assigment == 9:
            diff = self._decode_subframe(block_size, bits_per_sample + 1)
            right = self._decode_subframe(block_size, bits_per_sample)
            for i in range(block_size):
                diff[i] += right[i]
            return [diff, right]

        if channel_assigment == 10:
            mid = self._decode_subframe(block_size, bits_per_sample)
            side = self._decode_subframe(block_size, bits_per_sample + 1)
            left, right = [-1] * block_size, [-1] * block_size
            for i in range(block_size):
                left[i] = (((mid[i] << 1) | (side[i] & 1)) + side[i]) >> 1
                right[i] = (((mid[i] << 1) | (side[i] & 1)) - side[i]) >> 1
            return [left, right]

        raise ValueError(
            'Invalid chanel assigment: {}'.format(channel_assigment))

    def _decode_subframe(self, block_size: int,
                         bits_per_sample: int) -> List[int]:
        self._stream.read_uint(1)  # reserved bit
        subframe_type = self._stream.read_uint(6)

        wasted_bits_per_sample = self._stream.read_uint(1)
        if wasted_bits_per_sample == 1:
            while self._stream.read_uint(1) == 0:
                wasted_bits_per_sample += 1
        bits_per_sample -= wasted_bits_per_sample

        if subframe_type == 0:
            # CONSTANT subframe
            result = [self._stream.read_sint(bits_per_sample)] * block_size
        elif subframe_type == 1:
            # VERBATIM subframe
            result = [self._stream.read_sint(bits_per_sample)
                      for _ in range(block_size)]
        elif 8 <= subframe_type <= 12:
            result = self._decode_fixed_subframe(subframe_type - 8,
                                                 block_size, bits_per_sample)
        elif 32 <= subframe_type:
            result = self._decode_lpc_subframe(
                lpc_order=subframe_type - 31,
                block_size=block_size,
                bits_per_sample=bits_per_sample)
        else:
            raise ValueError('Invalid subframe type: {}'.format(subframe_type))

        if wasted_bits_per_sample > 0:
            return [(s << wasted_bits_per_sample) for s in result]
        return result

    def _decode_lpc_subframe(self, lpc_order: int, block_size: int,
                             bits_per_sample: int) -> List[int]:
        warmup_samples = [self._stream.read_sint(bits_per_sample)
                          for _ in range(lpc_order)]
        qlp_precision = self._stream.read_uint(4) + 1
        qlp_shift_needed = self._stream.read_sint(5)
        coefs = [self._stream.read_sint(qlp_precision)
                 for _ in range(lpc_order)]
        residuals = self._decode_residuals(block_size, lpc_order)

        result = warmup_samples + [-1] * len(residuals)
        for i in range(lpc_order, len(result)):
            residual = residuals[i - lpc_order]
            s = sum(coef * result[i - j - 1] for (j, coef) in enumerate(coefs))
            s >>= qlp_shift_needed
            result[i] = s + residual

        return result

    def _decode_fixed_subframe(self, lpc_order: int, block_size: int,
                               bits_per_sample: int) -> List[int]:
        warmup_samples = [self._stream.read_sint(bits_per_sample)
                          for _ in range(lpc_order)]
        coefs = FIXED_SUBFRAME_COEFFS[lpc_order]
        residuals = self._decode_residuals(block_size, lpc_order)

        result = warmup_samples + [-1] * len(residuals)
        for i in range(lpc_order, len(result)):
            residual = residuals[i - lpc_order]
            s = sum(coef * result[i - j - 1] for (j, coef) in enumerate(coefs))
            result[i] = s + residual

        return result

    def _decode_residuals(self, block_size: int,
                          predictor_order: int) -> List[int]:
        coding_method = self._stream.read_uint(2)
        if coding_method not in [0, 1]:
            raise ValueError('Invalid coding method: {}'.format(coding_method))
        rice_parameter_len = 4 if coding_method == 0 else 5
        rice_escape_code = 0b1111 if coding_method == 0 else 0b11111

        partion_order = self._stream.read_uint(4)
        partions_count = 1 << partion_order

        if block_size % partions_count != 0:
            raise ValueError('Block size is not devisible by '
                             'number of rice partions')

        result = []  # type: ignore
        for i in range(partions_count):
            samples_in_partion = block_size >> partion_order
            if i == 0:
                samples_in_partion -= predictor_order

            rice_parameter = self._stream.read_uint(rice_parameter_len)

            if rice_parameter == rice_escape_code:
                rice_parameter = self._stream.read_uint(5)

            result += [self._stream.read_rice_int(rice_parameter)
                       for _ in range(samples_in_partion)]

        return result
