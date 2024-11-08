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


# Protocol
## Packets
### `ERROR`
- **Enum Value**: `-1`
- **Description**: Sent to report errors.
- **Fields**: 
  - `message`: Error message.
  
### `CONNECT_REQUEST`
- **Enum Value**: `0`
- **Description**: Client requests to connect to a game.
- **Fields**: 
  - `game_id`: Game identifier.
  - `username`: Player's username.

### `CONNECT_RESPONSE`
- **Enum Value**: `1`
- **Description**: Server's response to a connection request.
- **Fields**: 
  - `player`: Player object.
  - `game`: Game object.

### `SYNC_GAME`
- **Enum Value**: `2`
- **Description**: Server syncs game state with clients.
- **Fields**: 
  - `game`: Game state.

### `FOUND_GAME`
- **Enum Value**: `3`
- **Description**: Server notifies client that a game is available to join.
- **Fields**: None.

### `MOVE`
- **Enum Value**: `4`
- **Description**: Player makes a move.
- **Fields**: 
  - `game_id`: Game identifier.
  - `index`: Move index.
  - `player`: Player making the move.

### `GAME_OVER`
- **Enum Value**: `5`
- **Description**: Game over, either a win or other condition.
- **Fields**: 
  - `game`: Finished game state.
  - `winner`: Player who won.


## Game Flow
1. **Client Connects**: 
   - Client sends a `ConnectRequest` with `game_id` and `username` to the server.

2. **Server Response**:
   - If the `game_id` is not associated with a game:
     - Server creates a new game and returns it to the client (client waits).
   - If the `game_id` exists:
     - Server assigns a second player and sends both players a `FoundGame` packet, assigning a random player the first turn.

3. **Game Sync and Play**:
   - Upon receiving the `FoundGame` packet:
     - Both clients sync with the server and the game starts.
   - **Player Moves**:
     - The first player sends a `Move` packet while the second player waits.
     - Upon receiving the move, the server sends both players a `SyncGame` packet.
   - This continues until a winner is determined.

4. **Game Over**:
   - Once a player wins, the server sends a `GameOver` packet.
   - Both clients disconnect and the server cleans up the game.
   - The server is now ready for the next game.


