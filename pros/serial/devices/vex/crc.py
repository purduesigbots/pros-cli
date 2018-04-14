from typing import *


class CRC:
    def __init__(self, size: int, polynomial: int):
        self._size = size
        self._polynomial = polynomial
        self._table = []

        for i in range(256):
            crc_accumulator = i << (self._size - 8)
            for j in range(8):
                if crc_accumulator & (1 << (self._size - 1)):
                    crc_accumulator = (crc_accumulator << 1) ^ self._polynomial
                else:
                    crc_accumulator = (crc_accumulator << 1)
            self._table.append(crc_accumulator)

    def compute(self, data: Iterable[int], accumulator: int = 0):
        for d in data:
            i = ((accumulator >> (self._size - 8)) ^ d) & 0xff
            accumulator = ((accumulator << 8) ^ self._table[i]) & ((1 << self._size) - 1)
        return accumulator
