from enum import IntEnum
from typing import Optional
from pydantic import BaseModel
import numpy as np


class ConnectCell(IntEnum):
    EMPTY = 0b00
    RED = 0b01
    YELLOW = 0b10
    BOUNDARY = 0b11

    def emoji(self) -> Optional[str]:
        match self:
            case self.EMPTY:
                return " "
            case self.RED:
                return ":red_circle:"
            case self.YELLOW:
                return ":yellow_circle:"

        raise ValueError(f"Can't display {self}")

    def __rich__(self) -> str:
        return self.emoji()


Board = list[list[ConnectCell]]


class ConnectFour(BaseModel):
    rows: int
    cols: int
    board: Board

    def __init__(
        self,
        rows: int = 6,
        cols: int = 7,
        board: Board = None,
        **args,
    ) -> None:
        if board is None:
            board = [[ConnectCell.EMPTY for _ in range(rows)] for _ in range(cols)]

        super().__init__(rows=rows, cols=cols, board=board, **args)

    def __rich__(self):
        from rich.table import Table

        t = Table(title="Connect Four", width=40)
        for c in range(self.cols):
            t.add_column(str(c))

        for row in reversed(range(self.rows)):
            t.add_row(*[self.get_piece(row, col) for col in range(self.cols)])

        return t

    def get_piece(self, row: int, col: int):
        if row >= self.rows:
            raise IndexError(
                f"Attempted to get row index {row} in a board with {self.rows}"
            )

        if col >= self.cols:
            raise IndexError(
                f"Attempted to get col index {col} in a board with {self.cols}"
            )

        return self.board[col][row]

    def drop_piece(self, col: int) -> bool: ...

    def check_win(self) -> bool: ...

    def __eq__(self, other):
        return np.array_equal(self.board, other.board)
