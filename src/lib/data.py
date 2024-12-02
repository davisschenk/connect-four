from pydantic import BaseModel
from uuid import UUID
from lib.connect_four import ConnectFour, ConnectCell
from typing import Optional
from enum import IntEnum
import asyncio


class Player(BaseModel):
    name: str
    id: UUID
    addr: tuple
    _writer: Optional[asyncio.StreamWriter] = None

    def get_color(self, game):
        if self.id == game.yellow_player.id:
            return ConnectCell.YELLOW
        elif self.id == game.red_player.id:
            return ConnectCell.RED

        raise ValueError("Player is not in game")


class GameState(IntEnum):
    REGISTRATION = 0
    DISCONNECTED = 1
    FINISHED = 2


class Game(BaseModel):
    state: GameState = GameState.REGISTRATION
    game_id: str
    red_player: Player
    yellow_player: Optional[Player]
    turn: UUID | None
    board: ConnectFour
