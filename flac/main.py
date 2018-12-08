from mimetypes import guess_extension
from os.path import isdir, join
from typing import List, Tuple

from argparser import make_parser
from meta import BitStream, Metadata
from song import Song


def decode_frame(stream: BitStream, chanels_count: int, bits_per_sample: int):
    sync_code = stream.read_uint(14)
    if sync_code != 0b11111111111110:
        raise ValueError('Invalid sync code')

    stream.read_uint(1)  # reserved bit
    stream.read_uint(1)  # block strategy
    block_size_code = stream.read_uint(4)
    sample_rate_code = stream.read_uint(4)
    channel_assigment = stream.read_uint(4)
    stream.read_uint(3)  # sample size
    stream.read_uint(1)  # reserved bit

    # TODO ???
    temp = stream.read_uint(8)
    while temp >= 0b11000000:
        stream.read_uint(8)
        temp = (temp << 1) & 0xFF

    if block_size_code == 1:
        block_size = 192
    elif 2 <= block_size_code <= 5:
        block_size = 576 << (block_size_code - 2)
    elif block_size_code == 6:
        block_size = stream.read_uint(8) + 1
    elif block_size_code == 7:
        block_size = stream.read_uint(16) + 1
    elif 8 <= block_size_code <= 15:
        block_size = 256 << (block_size_code - 8)

    if sample_rate_code == 12:
        stream.read_uint(8)
    elif sample_rate_code in [13, 14]:
        stream.read_uint(16)

    stream.read_uint(8)  # crc-8

    blocks = decode_subframes(stream, block_size, bits_per_sample,
                              channel_assigment)
    stream._clear_buffer()  # align to byte
    stream.read_uint(16)  # crc-16

    for b in blocks:
        assert len(b) == block_size


def decode_subframes(stream: BitStream, block_size: int, bits_per_sample: int,
                     channel_assigment: int) -> List[List[int]]:
    if 0 <= channel_assigment <= 7:
        return [decode_subframe(stream, block_size, bits_per_sample)
                for _ in range(channel_assigment + 1)]

    if channel_assigment == 8:
        left = decode_subframe(stream, block_size, bits_per_sample)
        diff = decode_subframe(stream, block_size, bits_per_sample + 1)
        for i in range(block_size):
            diff[i] = left[i] - diff[i]
        return [left, diff]

    if channel_assigment == 9:
        diff = decode_subframe(stream, block_size, bits_per_sample + 1)
        right = decode_subframe(stream, block_size, bits_per_sample)
        for i in range(block_size):
            diff[i] += right[i]
        return [diff, right]

    if channel_assigment == 1:
        mid = decode_subframe(stream, block_size, bits_per_sample)
        side = decode_subframe(stream, block_size, bits_per_sample)
        left, right = [-1] * block_size, [-1] * block_size
        for i in range(block_size):
            left[i] = (((mid[i] << 1) | (side[i] & 1)) + side[i]) >> 1
            right[i] = (((mid[i] << 1) | (side[i] & 1)) - side[i]) >> 1
        return [left, right]

    raise ValueError('Invalid chanel assigment')


def decode_subframe(stream: BitStream, block_size: int,
                    bits_per_sample: int) -> List[int]:
    stream.read_uint(1)  # reserved bit
    subframe_type = stream.read_uint(6)

    wasted_bits_per_sample = stream.read_uint(1)
    if wasted_bits_per_sample == 1:
        while stream.read_uint(1) == 0:
            wasted_bits_per_sample += 1
    bits_per_sample -= wasted_bits_per_sample

    if 32 <= subframe_type:
        result = decode_lpc_subframe(
            stream=stream,
            lpc_order=subframe_type - 31,
            block_size=block_size,
            bits_per_sample=bits_per_sample)
    else:
        raise ValueError('This subframe type not implemented yet')

    if wasted_bits_per_sample > 0:
        return [(s << wasted_bits_per_sample) for s in result]  # TODO имя s?
    return result


def decode_lpc_subframe(stream: BitStream, lpc_order: int,
                        block_size: int, bits_per_sample: int) -> List[int]:
    warmup_samples = [stream.read_sint(bits_per_sample)
                      for _ in range(lpc_order)]
    qlp_precision = stream.read_uint(4) + 1
    qlp_shift_needed = stream.read_sint(5)
    coefs = [stream.read_sint(qlp_precision) for _ in range(lpc_order)]
    residuals = decode_residuals(stream, block_size, lpc_order)

    result = warmup_samples + [-1] * len(residuals)
    for i in range(lpc_order, len(result)):
        residual = residuals[i - lpc_order]
        s = sum(coef * result[i - j - 1] for (j, coef) in enumerate(coefs))
        s >>= qlp_shift_needed
        result[i] = s + residual

    return result


def decode_residuals(stream: BitStream, block_size: int,
                     predictor_order: int) -> List[int]:
    coding_method = stream.read_uint(2)
    if coding_method not in [0, 1]:
        raise ValueError('Invalid coding method')
    rice_parameter_len = 4 if coding_method == 0 else 5
    rice_escape_code = 0b1111 if coding_method == 0 else 0b11111

    partion_order = stream.read_uint(4)
    partions_count = 1 << partion_order

    if block_size % partions_count != 0:
        raise ValueError('Block size is not devisible by '
                         'number of rice partions')

    result = []  # type: ignore
    for i in range(partions_count):
        samples_in_partion = block_size >> partion_order
        if i == 0:
            samples_in_partion -= predictor_order

        rice_parameter = stream.read_uint(rice_parameter_len)

        if rice_parameter == rice_escape_code:
            rice_parameter = stream.read_uint(5)

        result += [stream.read_rice_int(rice_parameter)
                   for _ in range(samples_in_partion)]

    return result


# if __name__ == '__main__':
#     with open('../sample16.flac', 'rb') as f:
#         f.read(839202)
#         stream = BitStream(f)
#         decode_frame(stream, 2, 16)


if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()

    # TODO сделай проверку на существование файла
    meta = Metadata(args.file)

    if args.command == 'info':
        print('\n' + meta.get_all_data(args.all))

    if args.command == 'play':
        song = Song(args.file)
        song.play()

    if args.command == 'covers':
        if not isdir(args.dir):
            raise FileNotFoundError('Directory does not exists')

        for i, pic in enumerate(meta.pictures):
            filename = join(args.dir, str(i))
            ext = guess_extension(pic.mime_type)
            if ext is not None:
                filename += ext

            with open(filename, 'wb') as f:
                f.write(pic.image_data)
