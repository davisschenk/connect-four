from pydantic import BaseModel
from uuid import UUID
from lib.connect_four import ConnectFour
from typing import Optional
from enum import IntEnum
import asyncio

class Player(BaseModel):
    name: str
    id: UUID
    addr: tuple[str, int]
    _writer: Optional[asyncio.StreamWriter] = None

class GameState(IntEnum):
    REGISTRATION = 0
    DISCONNECTED = 1

class Game(BaseModel):
    state: GameState = GameState.REGISTRATION
    game_id: str
    red_player: Player
    yellow_player: Optional[Player]
    turn: bool
    board: ConnectFour
