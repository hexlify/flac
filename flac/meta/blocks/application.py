from .metadata import MetadataBlock
from ..bit_stream import BitStream


class Application(MetadataBlock):
    def __init__(self, size: int, is_last: bool, stream: BitStream):
        super().__init__(size, is_last)

        self.id = stream.read_bytes(4).decode('utf-8')
        self.data = stream.read_bytes(size - 4)

    def __str__(self):
        return 'Application ID: {}'.format(self.id)
