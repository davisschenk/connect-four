# Connect Four

The game of Connect Four implemented as a TUI using Python and `sockets` for networking.

## **How to play:**
1. **Install Dependencies:** Use any tool capable of installing from a `pyproject.toml`
  - Install [UV](https://docs.astral.sh/uv/) and run `uv sync`
  - Install [just](https://github.com/casey/just) or run commands manually
2. **Start the server:** Run the `just server` script to start the server.
3. **Connect clients:** Run the `just client` script on two different machines or terminals.
4. **Play the game:** Players take turns entering their moves. The first player to get 4 in a row wins!

## **Technologies used:**
### Libraries
- Sockets
  Networking package from the standard library
- Unittest
  Unit testing package from the standard library
- [Textual](https://github.com/textualize/textual/)
  Python library designed for building nice TUI's

### Tooling
- [UV](https://docs.astral.sh/uv/)
  An awesome python project and dependency manager
- [Ruff](https://docs.astral.sh/ruff/)
  A fast tool for python formatting and checking
- Github Actions
  Automatically run tests to check code before committing to main
- [pre-commit](https://pre-commit.com/)
  Automatically fix code formatting before commiting
    
