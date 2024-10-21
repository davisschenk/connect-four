#!/usr/bin/env python3
from lib.packets import Packet, ConnectRequest, ConnectResponse, FoundGame, Error, SyncGame
from lib.data import Player, Game
from lib.connect_four import ConnectFour
import asyncio
import argparse
import logging
import uuid


logging.basicConfig(level=logging.INFO)

class ConnectFourServer:
    def __init__(self):
        # Mapping from game id to game
        self.games: dict[str, Game] = {}

        # Mapping from addr to game id
        self.connections: dict[tuple[str, int], str] = {}

    @classmethod
    async def get_packet(cls, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.readline()

        if data:        
            return Packet.from_json(data)
    
    
    @classmethod
    async def send(self, writer: asyncio.StreamWriter, packet: Packet):
        writer.write(packet.to_json().encode() + b"\n")
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info("peername")
        logging.info("Connection from %s", addr)

        while True:
            packet = await self.get_packet(reader, writer)

            if packet is None:
                logging.info(f"Connection lost {addr}")
                writer.close()
                await writer.wait_closed()
                break

            if isinstance(packet, ConnectRequest):
                self.connections[addr] = packet.game_id

                await self.handle_connect_request(writer, packet)

            if isinstance(packet, SyncGame):
                await self.handle_sync_game(writer, packet)
            print(packet)

    async def handle_connect_request(self,  writer: asyncio.StreamWriter, packet: ConnectRequest):
        game = self.games.get(packet.game_id)
        player = Player(name=packet.username, id=uuid.uuid4(), addr=writer.get_extra_info("peername"))
        player._writer = writer
        
        if game is None:
            self.games[packet.game_id] = Game(
                game_id=packet.game_id,
                red_player=player,
                yellow_player=None,
                turn=0,
                board=ConnectFour()
            )
        elif game.red_player and not game.yellow_player:
            logging.info("Sending FoundGame message")
            await self.send(game.red_player._writer, FoundGame())

            game.yellow_player = player
        else:
            await self.send(writer, Error(message="Game already full"))

        response = ConnectResponse(player=player, game=self.games[packet.game_id])
        await self.send(writer, response)

    async def handle_sync_game(self, writer: asyncio.StreamWriter, packet: ConnectRequest):
        addr = writer.get_extra_info("peername")
        game_id = self.connections.get(addr)

        if game_id is None:
            return await self.send(writer, Error(message="Not Registered"))

        await self.send(SyncGame(game=self.games[game_id]))



                
                

        
async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=60000)

    args = parser.parse_args()
    connect_four = ConnectFourServer()

    server = await asyncio.start_server(connect_four.handle_client, args.host, args.port)
    logging.info("Serving on %s", server.sockets[0].getsockname())

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())

