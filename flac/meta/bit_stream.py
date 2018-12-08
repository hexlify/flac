from bitstruct import unpack
from typing import BinaryIO


class BitStream:
    def __init__(self, stream: BinaryIO):
        self._stream = stream
        self._bitbuffer = 0
        self._bitbufferlen = 0

    def read_uint(self, n) -> int:
        """Считать слудующие n битов как unsigned int
        """
        while self._bitbufferlen < n:
            tmp = self._stream.read(1)
            if len(tmp) == 0:
                raise EOFError()
            tmp = tmp[0]  # type: ignore
            self._bitbuffer = (self._bitbuffer << 8) | tmp  # type: ignore
            self._bitbufferlen += 8
        self._bitbufferlen -= n
        result = (self._bitbuffer >> self._bitbufferlen) & ((1 << n) - 1)
        self._bitbuffer &= (1 << self._bitbufferlen) - 1
        return result

    def read_byte(self) -> int:
        """Считываем следующий байт. При необходимости выравниваем по байтам
        """
        if self._bitbufferlen >= 8:
            return self.read_uint(8)

        self._clear_buffer()
        result = self._stream.read(1)
        if len(result) == 0:
            return -1
        return result[0]

    # TODO протестируй
    def read_sint(self, n):
        """Считать следующие n битов как signed int
        """
        res = self.read_uint(n)
        res -= res >> (n - 1) << n
        return res

    def _clear_buffer(self):
        self._bitbuffer = 0
        self._bitbufferlen = 0
