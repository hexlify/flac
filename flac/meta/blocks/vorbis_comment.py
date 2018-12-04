import struct as byte

import bitstruct as bit

from .metadata import MetadataBlock


class VorbisComment(MetadataBlock):
    def __init__(self, length: int, is_last: bool, data: bytes):
        if len(data) != length or length < 0:
            raise ValueError()

        super().__init__(length, is_last)
        self.parse_comments(data)

    def parse_comments(self, data):
        vendor_length = byte.unpack('<I', data[:4])[0]
        self.vendor_string = data[4:4+vendor_length].decode('utf-8')
        comments_length = byte.unpack(
            '<I', data[4+vendor_length:8 + vendor_length])[0]

        index = 8 + vendor_length
        self.tags = {}
        for _ in range(comments_length):
            comment_length = byte.unpack('<I', data[index:index+4])[0]
            index += 4
            comment = data[index:index + comment_length].decode('utf-8')
            tag, value = comment.split('=')
            index += comment_length

            if tag not in self.tags:
                self.tags[tag] = []
            self.tags[tag].append(value)

    def __str__(self):
        s = 'Vendor string: {}'.format(self.vendor_string)
        for tag, values in self.tags.items():
            vals = ','.join(values)
            s += '\n{}: {}'.format(tag.capitalize(), vals)
        return s + '\n'
