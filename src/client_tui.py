import argparse

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static, Input, Button, Label
from textual.screen import Screen
from textual import work
import asyncio


class RegisterInputs(Static):
    CSS = """
    #start_game {
        content-align: center;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Game ID:")
        yield Input(placeholder="Enter your Game ID", id="game_id")

        yield Label("Username:")
        yield Input(placeholder="Enter your username", id="username")

        yield Button(label="Start Game", id="start_game")


class Registeration(Screen):
    CSS = """
    RegisterInputs {
        padding: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(name="Register")
        yield RegisterInputs()
        yield Footer()


class Game(Screen):
    def compose(self) -> ComposeResult:
        yield Header(name="Game")
        yield Static("GAME")
        yield Footer()


class ConnectFourApp(App):
    BINDINGS = [("q", "switch_mode('game')", "Quit")]
    MODES = {"registration": Registeration, "game": Game}
    CSS = """

    """

    def __init__(self, args) -> None:
        self.ip = args.ip
        self.port = args.port
        self.dns = args.dns

        super().__init__()

    @work(exclusive=True)
    async def network(self):
        while True:
            await asyncio.sleep(5)
            self.log("a")

    def on_mount(self) -> None:
        self.network()
        self.log("Mounted")
        self.switch_mode("registration")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Connect Four Client",
        epilog="Davis Schenkenberger",
    )
    parser.add_argument("-i", "--ip", help="IP address of the server")
    parser.add_argument("-p", "--port", help="listening port of the server")
    parser.add_argument("-n", "--dns", help="DNS name of the server")

    args = parser.parse_args()
    app = ConnectFourApp(args)
    app.run()
