from .metadata import MetadataBlock


class Application(MetadataBlock):
    def __init__(self, length: int, is_last: bool, data: bytes):
        if len(data) != length or length < 0:
            raise ValueError()

        super().__init__(length, is_last)
        self.id = data[:4].decode('utf-8')
        self.data = data[4:]

    def __str__(self):
        return f'Application ID: {self.id}\n'
