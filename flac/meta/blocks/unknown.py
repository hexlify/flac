from ..bit_stream import BitStream
from .metadata import MetadataBlock


class Unknown(MetadataBlock):
    def __init__(self, size: int, is_last: bool, stream: BitStream):
        super().__init__(size, is_last)

        stream.read_bytes(size)
