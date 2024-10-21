from enum import Enum
from pydantic import BaseModel


class Packets(Enum):
    CONNECT = 0
    JOIN_GAME = 1
    MOVE = 2
    GAME_STATE = 3


class Packet(BaseModel):
    packet: Packets


class GetBoard(Packet): ...
