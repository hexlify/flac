from struct import unpack

from ..bit_stream import BitStream
from .metadata import MetadataBlock


picture_types = {
    0: "Other",
    1: "32x32 pixels 'file icon' (PNG only)",
    2: "Other file icon",
    3: "Cover (front)",
    4: "Cover (back)",
    5: "Leaflet page",
    6: "Media (e.g. label side of CD)",
    7: "Lead artist/lead performer/soloist",
    8: "Artist/performer",
    9: "Conductor",
    10: "Band/Orchestra",
    11: "Composer",
    12: "Lyricist/text writer",
    13: "Recording Location",
    14: "During recording",
    15: "During performance",
    16: "Movie/video screen capture",
    17: "A bright coloured fish",
    18: "Illustration",
    19: "Band/artist logotype",
    20: "Publisher/Studio logotype",
}


class Picture(MetadataBlock):
    def __init__(self, size: int, is_last: bool, stream: BitStream):
        super().__init__(size, is_last)

        self.parse_picture(stream)

    def parse_picture(self, stream: BitStream):
        self.type = picture_types[stream.read_uint(32)]

        mime_len = stream.read_uint(32)
        self.mime_type = stream.read_bytes(mime_len).decode('utf-8')

        desc_len = stream.read_uint(32)
        self.description = stream.read_bytes(desc_len).decode('utf-8')

        self.width = stream.read_uint(32)
        self.height = stream.read_uint(32)
        self.color_depth = stream.read_uint(32)
        self.used_colors = stream.read_uint(32)

        image_len = stream.read_uint(32)
        self.image_data = stream.read_bytes(image_len)

    def __str__(self):
        s = 'Type: {}\n'.format(self.type)
        s += 'Mime type: {}\n'.format(self.mime_type)
        s += 'Description: {}\n'.format(self.description)
        s += 'Width: {}\n'.format(self.width)
        s += 'Height: {}\n'.format(self.height)
        s += 'Color depth: {}\n'.format(self.color_depth)
        s += 'Used colors: {}\n'.format(self.used_colors)
        return s
