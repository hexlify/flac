from struct import unpack

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


def _substr(data: bytes, start: int, length: int):
    return data[start:start+length]


class Picture(MetadataBlock):
    def __init__(self, length: int, is_last: bool, data: bytes):
        if len(data) != length or length < 0:
            raise ValueError()

        super().__init__(length, is_last)
        self.parse_picture(data)

    def parse_picture(self, data):
        self.type = picture_types[unpack('>I', _substr(data, 0, 4))[0]]

        mime_len = unpack('>I', _substr(data, 4, 4))[0]
        self.mime_type = _substr(data, 8, mime_len).decode('utf-8')

        desc_len = unpack('>I', _substr(data, 8 + mime_len, 4))[0]
        self.description = _substr(
            data, 12 + mime_len, desc_len).decode('utf-8')

        (self.width, self.height, self.color_depth, self.used_colors,
         _) = unpack('>IIIII', _substr(data, 12+mime_len+desc_len, 20))

        self.image_data = data[32+mime_len+desc_len:]

    def __str__(self):
        s = f'Type: {self.type}\n'
        s += f'Mime type: {self.mime_type}\n'
        s += f'Description: {self.description}\n'
        s += f'Width: {self.width}\n'
        s += f'Height: {self.height}\n'
        s += f'Color depth: {self.color_depth}\n'
        s += f'Used colors: {self.used_colors}\n'
        return s
