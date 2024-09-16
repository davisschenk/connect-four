[private]
default:
    @just -l

server:
    uv run src/server.py

client:
    uv run src/client.py