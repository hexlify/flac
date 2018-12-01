from block_type import BlockType


class MetadataBlock:
    def __init__(self, s: BlockType, length: int, is_last: bool, data: bytes):
        self.type = s
        self.length = length
        self.is_last = is_last
        self.data = data
