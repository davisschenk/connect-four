#!/usr/bin/env python3
import selectors
import socket
import argparse
import logging

sel = selectors.DefaultSelector()


class ConnectFourServer:
    def accept_message(self, conn, addr): ...


server = ConnectFourServer()


def accept_wrapper(sock):
    conn, addr = sock.accept()

    logging.info("Accepted connection from", addr)

    conn.setblocking(False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host")
    parser.add_argument("--port")

    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
    sock.bind((args.host, args.port))
    sock.listen()
    sock.setblocking(False)
    sel.register(sock, selectors.EVENT_READ)

    while True:
        events = sel.select(timeout=None)

        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
