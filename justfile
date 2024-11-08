[private]
default:
    @just -l

server *args:
    @uv run src/server.py {{args}}

client *args:
    @uv run src/client_text.py {{args}}

test:
    @uv run python -m unittest discover -s "src"