from enum import Enum
from typing import Self
import struct


class ConnectCell(Enum):
    EMPTY = 0b00
    RED = 0b01
    YELLOW = 0b10

    def emoji(self):
        match self:
            case self.EMPTY:
                return " "
            case self.RED:
                return ":red_circle:"
            case self.YELLOW:
                return ":yellow_circle:"

    def __rich__(self) -> str:
        return self.emoji()

class ConnectFour:
    def __init__(self, rows=6, cols=7) -> None:
        self.rows = rows
        self.cols = cols
        self.board = [
            [ConnectCell.EMPTY for _ in range(cols)] 
            for _ in range(rows)
        ]

    def pack(self) -> str:
        packed = bytearray()
        packed.extend(struct.pack(">BB", self.rows, self.cols))


        for row in self.board:
            for cell in row:
                packed.extend(struct.pack("B", cell.value))

        return packed.hex()

    @classmethod
    def unpack(cls, value: str) -> Self:
        value = bytearray.fromhex(value)
        rows, cols = struct.unpack(">BB", value[:2])
        empty = cls(rows=rows, cols=cols)

        for row in range(rows):
            for col in range(cols):
                cell_value = struct.unpack_from("B", value, 2 + (row * cols) + col)[0]
                empty.board[row][col] = ConnectCell(cell_value)

        return empty