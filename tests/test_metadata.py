import io
import unittest

from flac.meta import BitStream
from flac.meta.blocks import Application, Picture, Streaminfo, VorbisComment


def create_stream(data: bytes) -> BitStream:
    return BitStream(io.BytesIO(data))


class StreaminfoTest(unittest.TestCase):
    def test_simple_parsing(self):
        data = (b'\x04\x80\x04\x80\x00\x06r\x00\x17\xf2\x17p\x03p\x00:i\x80'
                b'\xe5\xd1\x00\xc6?Q\x88\x90\x0cf\xb6\xa6\xa0\x8c\xe2\xeb')

        s = Streaminfo(len(data), False, create_stream(data))

        self.assertEqual(s.min_block_size, 1152)
        self.assertEqual(s.max_block_size, 1152)
        self.assertEqual(s.min_frame_size, 1650)
        self.assertEqual(s.max_frame_size, 6130)
        self.assertEqual(s.sample_rate, 96000)
        self.assertEqual(s.channels, 2)
        self.assertEqual(s.bits_per_sample, 24)
        self.assertEqual(s.total_samples, 3828096)
        self.assertEqual(s.md5, data[18:])


class VorbisCommentTest(unittest.TestCase):
    def test_simple_parsing(self):
        data = (
            b'&\x00\x00\x00reference libFLAC 1.2.1 win64 20080709\x05\x00\x00'
            b'\x00\x0f\x00\x00\x00ALBUM=Bee Moved\x0f\x00\x00\x00TITLE=Bee Mov'
            b'ed\x1a\x00\x00\x00ALBUMARTIST=Blue Monday FM\x06\x00\x00\x00MRAT'
            b'=0\x15\x00\x00\x00ARTIST=Blue Monday FM')
        vc = VorbisComment(len(data), False, create_stream(data))

        self.assertEqual(vc.vendor_string,
                         'reference libFLAC 1.2.1 win64 20080709')
        self.assertDictEqual(
            vc.tags,
            {
                'ALBUM': ['Bee Moved'],
                'TITLE': ['Bee Moved'],
                'MRAT': ['0'],
                'ALBUMARTIST': ['Blue Monday FM'],
                'ARTIST': ['Blue Monday FM'],
            })

    def test_with_multiple_tag_values(self):
        data = (
            b'\x20\x00\x00\x00reference libFLAC 1.2.1 20141125\x10\x00\x00\x00'
            b'\x11\x00\x00\x00ALBUM=REFLECTIONS\x1e\x00\x00\x00ALBUMARTIST=Tro'
            b'ndheimSolistene\x19\x00\x00\x00ARTIST=TrondheimSolistene\x15\x00'
            b'\x00\x00BARCODE=7041888521525\x1b\x00\x00\x00CATALOGNUMBER=70418'
            b'88521525I\x00\x00\x00COMMENT=Generated by Merging Technologies A'
            b'lbum Publishing\nLabel Code: 2L\x19\x00\x00\x00COMPOSER=Benjamin'
            b' Britten\t\x00\x00\x00DATE=2016\x0c\x00\x00\x00DISCNUMBER=1/\x00'
            b'\x00\x00ENCODEDBY=Merging Technologies Album Publishing\x0f\x00'
            b'\x00\x00GENRE=Classical\t\x00\x00\x00GENRE=Rap\n\x00\x00\x00GENR'
            b'E=Rock\x11\x00\x00\x00ISRC=NOMPP1603040\x08\x00'
            b'\x00\x00LABEL=2L)\x00\x00\x00TITLE=Frank Bridge Variations: 4. R'
            b'omance\r\x00\x00\x00TRACKNUMBER=4\r\x00\x00\x00TRACKTOTAL=22')
        vc = VorbisComment(len(data), False, create_stream(data))

        self.assertEqual(vc.vendor_string, 'reference libFLAC 1.2.1 20141125')
        self.assertListEqual(
            vc.tags['GENRE'],
            ['Classical', 'Rap', 'Rock'])


class PictureTest(unittest.TestCase):
    def test_simple_parsing(self):
        data = (
            b'\x00\x00\x00\x03\x00\x00\x00\nimage/jpeg\x00\x00\x00\x0bFront Co'
            b'ver\x00\x00\x04\xb0\x00\x00\x04\xb0\x00\x00\x00\x18\x00\x00\x00'
            b'\x00\x00\n"C\xff\xd8')
        pic = Picture(len(data), False, create_stream(data))

        self.assertEqual(pic.type, 'Cover (front)')
        self.assertEqual(pic.mime_type, 'image/jpeg')
        self.assertEqual(pic.description, 'Front Cover')
        self.assertEqual(pic.height, 1200)
        self.assertEqual(pic.width, 1200)
        self.assertEqual(pic.color_depth, 24)
        self.assertEqual(pic.used_colors, 0)
        self.assertEqual(pic.image_data, b'\xff\xd8')


class ApplicationTest(unittest.TestCase):
    def test_simple_parsing(self):
        data = b'SONYapplicationdata'
        app = Application(len(data), False, create_stream(data))

        self.assertEqual(app.id, 'SONY')
        self.assertEqual(app.data, b'applicationdata')
