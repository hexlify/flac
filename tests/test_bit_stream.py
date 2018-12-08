import unittest
import io
import struct

from flac.meta import BitStream


class BitStreamTest(unittest.TestCase):
    def setUp(self):
        data = struct.pack('>BBB', 0b11100101, 0b01100001, 0b00001111)
        stream = io.BytesIO(data)
        self.stream = BitStream(stream)

    def test_read_uint(self):
        self.assertEqual(self.stream.read_uint(3), 0b111)
        self.assertEqual(self.stream.read_uint(8), 0b00101011)
        self.assertEqual(self.stream.read_uint(1), 0)

    def test_stream_should_store_rest_in_buffer(self):
        self.stream.read_uint(5)
        self.assertEqual(self.stream._bitbuffer, 0b101)
        self.assertEqual(self.stream._bitbufferlen, 3)

    def test_read_byte(self):
        self.assertEqual(self.stream.read_byte(), 0b11100101)

    def test_read_byte_should_clear_buffer_and_align_on_byte(self):
        self.stream.read_uint(5)
        self.assertEqual(self.stream.read_byte(), 0b01100001)
        self.assertEqual(self.stream._bitbuffer, 0)
        self.assertEqual(self.stream._bitbufferlen, 0)

    def test_reading_rice_encoded_int(self):
        data = 0b00001010101010111000010111010000.to_bytes(4, byteorder='big')
        stream = BitStream(io.BytesIO(data))

        self.assertEqual(stream.read_rice_int(4), -35)
        self.assertEqual(stream.read_rice_int(4), -11)
        self.assertEqual(stream.read_rice_int(4), +4)
        self.assertEqual(stream.read_rice_int(4), -12)
        self.assertEqual(stream.read_rice_int(4), 8)
