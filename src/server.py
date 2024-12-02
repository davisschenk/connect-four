#!/usr/bin/env python3
from lib.packets import Packet, ConnectRequest, ConnectResponse, FoundGame, Error, SyncGame, Move, GameOver, ConnectionLost
from lib.data import GameState, Player, Game
from lib.connect_four import ConnectFour, ConnectCell
import asyncio
import argparse
from loguru import logger
import uuid
import random
import sys
import ssl
from pathlib import Path

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
            logger.error("Connection reset")
            return None

        if data:
            try:
                packet = Packet.from_json(data)
                logger.debug("Recieved packet: {}", packet)
                return packet
            except Exception as e:
                logger.info("Received bad packet: {}", e)
                await cls.send(writer, Error(message=str(e)))
                return False

    @classmethod
    async def send(self, writer: asyncio.StreamWriter, packet: Packet):
        logger.debug("Sending packet to {}: {}", writer.get_extra_info("peername"), packet)
        writer.write(packet.to_json().encode() + b"\n")

    @classmethod
    async def broadcast(self, game: Game, packet: Packet):
        await self.send(game.red_player._writer, packet)
        await self.send(game.yellow_player._writer, packet)

    async def remove_game(self, addr):
        if game_id := self.connections.get(addr):
            if game := self.games.get(game_id):
                try:
                    await self.broadcast(game, ConnectionLost())
                    await self.close_writer(game.red_player._writer)
                    await self.close_writer(game.yellow_player._writer)
                    del self.games[game_id]
                    logger.info("Removed game {}", game_id)
                except Exception as e:
                    logger.debug("Bypassing error while removing game: {}", e)

            return True
        return False

    async def close_writer(self, writer):
        try:
            writer.close()
            await writer.wait_closed()
        except ssl.SSLError:
            pass

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info("peername")
        logger.info("Connection from {}", addr)

        while True:
            packet = await self.get_packet(reader, writer)

            if packet is None:
                logger.info("Connection lost {}", addr)
                await self.close_writer(writer)
                await self.remove_game(addr)
                break

            if not packet:
                continue

            if isinstance(packet, ConnectRequest):
                self.connections[addr] = packet.game_id

                await self.handle_connect_request(writer, packet)

            if isinstance(packet, SyncGame):
                await self.handle_sync_game(writer, packet)

            if isinstance(packet, Move):
                if winner := await self.handle_move(writer, packet):
                    logger.info("{} won there game in lobby {}", winner, packet.game_id)
                    await self.remove_game(addr)
                    break

        logger.info("Closing connection {}", addr)
        await self.close_writer(writer)

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
            game.state = GameState.FINISHED
            await self.broadcast(game, GameOver(game=game, winner=player))
            return player

        await self.broadcast(game, SyncGame(game=game))
        return None


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", "-p", type=int, default=60000)
    parser.add_argument("--debug", type=str, default="INFO", help="Logging debug level")
    parser.add_argument("--ssl-cert", type=Path, default=Path("certs/fullchain.pem"), help="Path to ssl certificate")
    parser.add_argument("--ssl-key", type=Path, default=Path("certs/privkey.pem"), help="Path to SSL private key")
    parser.add_argument("--ssl", action=argparse.BooleanOptionalAction, default=True, help="Options to enable or disable SSL")

    args = parser.parse_args()

    connect_four = ConnectFourServer()

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(args.ssl_cert, args.ssl_key)

    server_args = {}
    if args.ssl:
        server_args["ssl"] = ssl_context

    server = await asyncio.start_server(connect_four.handle_client, args.host, args.port, **server_args)
    logger.info("Serving on {}", server.sockets[0].getsockname())

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
