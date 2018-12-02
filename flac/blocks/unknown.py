from .metadata import MetadataBlock


class Unknown(MetadataBlock):
    def __init__(self, length: int, is_last: bool, data: bytes):
        super().__init__(length, is_last)
