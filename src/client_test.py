#!/usr/bin/env python3
from lib.packets import Packet, ConnectRequest, ConnectResponse, Error
import asyncio
import argparse
import logging
from aioconsole import ainput


logging.basicConfig(level=logging.INFO)

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
        logging.info(f"Connected to {self.host}:{self.port}")

    async def get_packet(self):
        data = await self.reader.readline()
        if not data:
            logging.info("Connection to server closed")
            self.writer.close()
            return await self.writer.wait_closed()
        
        return Packet.from_json(data)
    
    async def send(self, packet: Packet):
        self.writer.write(packet.to_json().encode() + b"\n")
        await self.writer.drain()

        return await self.get_packet()
    
    async def play(self):
        await self.connect()
        connected = False
        
        while not connected:
            username = await ainput("Username: ")
            game_id = await ainput("Game ID: ")

            response = await self.connect_request(username, game_id)
            if isinstance(response, ConnectResponse):
                self.player = response.player
                self.game = response.game
                connected = True
            elif isinstance(response, Error):
                logging.error(f"Error while match making: {response}")

        while True:
            packet = await self.get_packet()

            print(packet)

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

