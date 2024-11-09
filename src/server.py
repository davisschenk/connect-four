#!/usr/bin/env python3
from lib.packets import (
    Packet,
    ConnectRequest,
    ConnectResponse,
    FoundGame,
    Error,
    SyncGame,
    Move,
    GameOver,
)
from lib.data import Player, Game
from lib.connect_four import ConnectFour, ConnectCell
import asyncio
import argparse
from loguru import logger
import uuid
import random
import sys

logger.remove(0)
logger.add(sys.stderr, format="<green>{time}</green> <level>{level}</level> - {message}", level="INFO", colorize=True)


class ConnectFourServer:
    def __init__(self):
        # Mapping from game id to game
        self.games: dict[str, Game] = {}

        # Mapping from addr to game id
        self.connections: dict[tuple[str, int], str] = {}

    @classmethod
    async def get_packet(cls, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            data = await reader.readline()
        except ConnectionResetError:
            return None

        if data:
            packet = Packet.from_json(data)
            logger.debug("Recieved packet: {}", packet)
            return packet

    @classmethod
    async def send(self, writer: asyncio.StreamWriter, packet: Packet):
        logger.debug("Sending packet to {}: {}", writer.get_extra_info("peername"), packet)
        writer.write(packet.to_json().encode() + b"\n")

    @classmethod
    async def broadcast(self, game: Game, packet: Packet):
        await self.send(game.red_player._writer, packet)
        await self.send(game.yellow_player._writer, packet)

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info("peername")
        logger.info("Connection from {}", addr)

        while True:
            packet = await self.get_packet(reader, writer)

            if packet is None:
                logger.info("Connection lost {}", addr)
                writer.close()
                await writer.wait_closed()

                if game_id := self.connections.get(addr):
                    logger.info("Removing game {}", game_id)
                    del self.games[game_id]
                break

            if isinstance(packet, ConnectRequest):
                self.connections[addr] = packet.game_id

                await self.handle_connect_request(writer, packet)

            if isinstance(packet, SyncGame):
                await self.handle_sync_game(writer, packet)

            if isinstance(packet, Move):
                await self.handle_move(writer, packet)

    async def handle_connect_request(self, writer: asyncio.StreamWriter, packet: ConnectRequest):
        game = self.games.get(packet.game_id)
        player = Player(
            name=packet.username,
            id=uuid.uuid4(),
            addr=writer.get_extra_info("peername"),
        )
        player._writer = writer

        if game is None:
            self.games[packet.game_id] = Game(
                game_id=packet.game_id,
                red_player=player,
                yellow_player=None,
                turn=None,
                board=ConnectFour(),
            )
            response = ConnectResponse(player=player, game=self.games[packet.game_id])
            await self.send(writer, response)
        elif game.red_player and not game.yellow_player:
            response = ConnectResponse(player=player, game=self.games[packet.game_id])
            await self.send(writer, response)
            game.yellow_player = player
            await self.broadcast(game, FoundGame())

            game.turn = random.choice([game.yellow_player.id, game.red_player.id])
            await self.broadcast(game, SyncGame(game=game))
        else:
            await self.send(writer, Error(message="Game already full"))

    async def handle_sync_game(self, writer: asyncio.StreamWriter, packet: ConnectRequest):
        addr = writer.get_extra_info("peername")
        game_id = self.connections.get(addr)

        if game_id is None:
            return await self.send(writer, Error(message="Not Registered"))

        await self.send(SyncGame(game=self.games[game_id]))

    async def handle_move(self, writer, packet: Move):
        game = self.games[packet.game_id]

        if game.turn == game.red_player.id:
            game.turn = game.yellow_player.id
            color = ConnectCell.RED
        else:
            color = ConnectCell.YELLOW
            game.turn = game.red_player.id

        game.board.drop_piece(packet.index, color)

        if winner := game.board.check_win():
            player = game.red_player if winner == ConnectCell.RED else game.yellow_player
            await self.broadcast(game, GameOver(game=game, winner=player))

        await self.broadcast(game, SyncGame(game=game))


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=60000)
    parser.add_argument("--debug", type=str, default="INFO")

    args = parser.parse_args()

    connect_four = ConnectFourServer()

    server = await asyncio.start_server(connect_four.handle_client, args.host, args.port)
    logger.info("Serving on {}", server.sockets[0].getsockname())

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
