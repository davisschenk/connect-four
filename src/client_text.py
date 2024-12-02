#!/usr/bin/env python3
from lib.packets import Packet, ConnectRequest, ConnectResponse, Error, FoundGame, SyncGame, Move, GameOver, ConnectionLost
import asyncio
import argparse
from loguru import logger
from aioconsole import ainput
from rich import print
import sys
import ssl
from pathlib import Path
import os

logger.remove(0)
logger.add(sys.stderr, format="<green>{time}</green> <level>{level}</level> - {message}", level="INFO", colorize=True)


class ConnectFourClient:
    def __init__(self, host: str, port: int, ssl_cert: Path):
        self.reader = None
        self.writer = None
        self.host = host
        self.port = port
        self.game = None
        self.player = None
        self.ssl_context = None
        self.ssl_cert = ssl_cert

    async def connect(self):
        if self.ssl_cert:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self.ssl_context.load_verify_locations(self.ssl_cert)
            self.ssl_context.verify_mode = ssl.CERT_REQUIRED
            self.ssl_context.check_hostname = False

        self.reader, self.writer = await asyncio.open_connection(self.host, self.port, ssl=self.ssl_context)
        logger.info("Connected to {}:{}", self.host, self.port)

    async def get_packet(self):
        data = await self.reader.readline()
        if not data:
            logger.info("Connection to server closed")
            self.writer.close()
            return await self.writer.wait_closed()

        packet = Packet.from_json(data)
        logger.debug("Received packet from server {}", packet.packet_type)
        return packet

    async def send(self, packet: Packet, wait=True):
        self.writer.write(packet.to_json().encode() + b"\n")
        await self.writer.drain()

        if wait:
            return await self.get_packet()

    async def register(self):
        registered = False

        while not registered:
            username = await ainput("Username: ")
            game_id = await ainput("Game ID: ")

            response = await self.connect_request(username, game_id)
            if isinstance(response, ConnectResponse):
                self.player = response.player
                self.game = response.game
                registered = True
            elif isinstance(response, Error):
                logger.error(f"Error while match making: {response}")

    async def wait_for_game(self):
        while True:
            packet = await self.get_packet()

            if isinstance(packet, FoundGame):
                return True

            logger.warning("Unexpected packet while waiting for game: {}", packet)

        return False

    async def get_move(self):
        while True:
            move = await ainput("Move > ")
            try:
                move = int(move)
            except ValueError:
                print("Enter a valid integer")
                continue

            if move not in range(0, self.game.board.cols):
                print("Enter a valid column")
                continue

            if not self.game.board.drop_piece(move, self.player.get_color(self.game)):
                print(f"The piece cannot be dropped in column {move}")
                continue

            return move

    async def game_loop(self):
        get_packet = True
        while True:
            logger.debug("Waiting for a packet")
            if get_packet:
                packet = await self.get_packet()
                if packet is None:
                    break
            else:
                get_packet = True

            if isinstance(packet, ConnectionLost):
                print("Connection to opponent lost, aborting game")
                break

            if isinstance(packet, SyncGame):
                self.game = packet.game

            os.system("clear")
            opponent = self.game.yellow_player if self.game.red_player.id == self.player.id else self.game.red_player
            print("[bold]Players:[/bold]")
            print(self.player.get_color(self.game), "[bold]" + self.player.name + "[/bold]")
            print(opponent.get_color(self.game), opponent.name)

            if isinstance(packet, GameOver):
                self.game = packet.game

                print(self.game.board)

                if self.player.id == packet.winner.id:
                    print("You won!")
                else:
                    print("Sorry you lost :(")

                break

            print(self.game.board)

            if self.game.turn == self.player.id:
                packet_task = asyncio.create_task(self.get_packet())
                move_task = asyncio.create_task(self.get_move())
                tasks = [packet_task, move_task]

                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

                for p in pending:
                    p.cancel()
                    try:
                        await p
                    except asyncio.CancelledError:
                        pass

                for d in done:
                    if d == tasks[0]:
                        packet = d.result()
                        get_packet = False
                        logger.debug("Packet recieved while making move: {}", packet)

                    elif d == tasks[1]:
                        move = d.result()
                        logger.info("Made move: {}", move)
                        await self.send(
                            Move(index=move, player=self.player, game_id=self.game.game_id),
                            wait=False,
                        )

            else:
                print("Waiting for the next player!")

        try:
            self.writer.close()
            await self.writer.wait_closed()
        except ssl.SSLError:
            pass

    async def play(self):
        await self.connect()

        await self.register()

        print("Waiting for opponent")
        await self.wait_for_game()

        logger.info("Game started")
        await self.game_loop()

    async def connect_request(self, username, game_id):
        packet = ConnectRequest(game_id=game_id, username=username)

        return await self.send(packet)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", "-i", default="localhost", help="Server hostname or IP")
    parser.add_argument("--port", "-p", type=int, default=60000, help="Server port")
    parser.add_argument("--ssl-cert", type=Path, default=Path("certs/fullchain.pem"), help="SSL certificate path")
    parser.add_argument("--ssl", action=argparse.BooleanOptionalAction, default=True, help="Options to enable or disable SSL")

    args = parser.parse_args()
    connect_four = ConnectFourClient(args.host, args.port, args.ssl_cert if args.ssl else None)
    await connect_four.play()


if __name__ == "__main__":
    asyncio.run(main())
