from enum import IntEnum
from pydantic import BaseModel, Field
from lib.data import Player, Game
import json


class Packets(IntEnum):
    ERROR = -1
    CONNECT_REQUEST = 0
    CONNECT_RESPONSE = 1
    SYNC_GAME = 2
    FOUND_GAME = 3
    MOVE = 4
    GAME_OVER = 5
    CONNECT_LOST = 6


class Packet(BaseModel):
    packet_type: Packets = Field(default=Packets.CONNECT_REQUEST)

    def to_json(self):
        return self.model_dump_json()

    @classmethod
    def from_json(cls, data):
        data = json.loads(data)
        packet_type = data.get("packet_type")
        if packet_type is None:
            raise ValueError("Packet does not contain a packet_type")

        packet_class = PACKET_MAPPING.get(packet_type)
        if packet_class is None:
            raise ValueError("packet_type not included in PACKET_MAPPING")

        return packet_class(**data)


class FoundGame(Packet):
    packet_type: Packets = Packets.FOUND_GAME


class ConnectRequest(Packet):
    packet_type: Packets = Packets.CONNECT_REQUEST
    # Lobby name
    game_id: str
    # Player name
    username: str


class ConnectResponse(Packet):
    packet_type: Packets = Packets.CONNECT_RESPONSE
    # Clients player
    player: Player
    game: Game


class Error(Packet):
    packet_type: Packets = Packets.ERROR
    message: str


class SyncGame(Packet):
    packet_type: Packets = Packets.SYNC_GAME
    game: Game


class Move(Packet):
    packet_type: Packets = Packets.MOVE
    game_id: str
    index: int
    player: Player


class GameOver(Packet):
    packet_type: Packets = Packets.GAME_OVER
    game: Game
    winner: Player


class ConnectionLost(Packet):
    packet_type: Packets = Packets.CONNECT_LOST


PACKET_MAPPING = {
    Packets.ERROR: Error,
    Packets.CONNECT_REQUEST: ConnectRequest,
    Packets.CONNECT_RESPONSE: ConnectResponse,
    Packets.SYNC_GAME: SyncGame,
    Packets.FOUND_GAME: FoundGame,
    Packets.MOVE: Move,
    Packets.GAME_OVER: GameOver,
    Packets.CONNECT_LOST: ConnectionLost,
}
