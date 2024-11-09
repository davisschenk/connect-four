#!/usr/bin/env python3
from lib.packets import (
    Packet,
    ConnectRequest,
    ConnectResponse,
    Error,
    FoundGame,
    SyncGame,
    Move,
    GameOver,
)
import asyncio
import argparse
from loguru import logger
from aioconsole import ainput
from rich import print
import sys


logger.remove(0)
logger.add(sys.stderr, format="<green>{time}</green> <level>{level}</level> - {message}", level="INFO", colorize=True)


class ConnectFourClient:
    def __init__(self, host: str, port: int):
        self.reader = None
        self.writer = None
        self.host = host
        self.port = port
        self.game = None
        self.player = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
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

    async def play(self):
        await self.connect()
        connected = False
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

        print("Waiting for opponent")
        while not connected:
            packet = await self.get_packet()

            if isinstance(packet, FoundGame):
                connected = True

        logger.info("Game started")

        while True:
            logger.debug("Waiting for a packet")
            packet = await self.get_packet()

            if isinstance(packet, SyncGame):
                self.game = packet.game

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
                print("Its my turn!")
                making_moves = False
                while not making_moves:
                    move = await ainput("Move > ")
                    try:
                        move = int(move)
                    except ValueError:
                        print("Enter a valid integer")
                        continue

                    if move not in range(0, self.game.board.cols):
                        print("Enter a valid column")
                        continue

                    making_moves = True

                await self.send(
                    Move(index=move, player=self.player, game_id=self.game.game_id),
                    wait=False,
                )
            else:
                print("Waiting for the next player!")

        self.writer.close()
        await self.writer.wait_closed()

    async def connect_request(self, username, game_id):
        packet = ConnectRequest(game_id=game_id, username=username)

        return await self.send(packet)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=60000)

    args = parser.parse_args()
    connect_four = ConnectFourClient(args.host, args.port)
    await connect_four.play()


if __name__ == "__main__":
    asyncio.run(main())
