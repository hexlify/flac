from struct import unpack

from ..bit_stream import BitStream
from .metadata import MetadataBlock


class VorbisComment(MetadataBlock):
    def __init__(self, size: int, is_last: bool, stream: BitStream):
        super().__init__(size, is_last)

        self.parse_comments(stream)

    def parse_comments(self, stream: BitStream):
        vendor_length = unpack("<I", stream.read_bytes(4))[0]
        self.vendor_string = stream.read_bytes(vendor_length).decode('utf-8')

        comments_length = unpack("<I", stream.read_bytes(4))[0]
        self.tags = {}  # type: ignore

        for _ in range(comments_length):
            comment_length = unpack("<I", stream.read_bytes(4))[0]
            comment = stream.read_bytes(comment_length).decode('utf-8')
            tag, value = comment.split('=')

            if tag not in self.tags:
                self.tags[tag] = []
            self.tags[tag].append(value)

    def __str__(self):
        s = 'Vendor string: {}'.format(self.vendor_string)
        for tag, values in self.tags.items():
            vals = ','.join(values)
            s += '\n{}: {}'.format(tag.capitalize(), vals)
        return s
