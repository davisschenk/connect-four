import argparse

from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header, Static


class ConnectFour(Static):
    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "column"

        table.add_columns(*[Text(str(i)) for i in range(1, 8)])
        for _ in range(6):
            row = [Text(":red_heart:") for column_i in range(7)]
            table.add_row(*row)

    def compose(self) -> ComposeResult:
        yield DataTable(id="connect-four")


class ConnectFourApp(App):
    def __init__(self, args) -> None:
        self.ip = args.ip
        self.port = args.port
        self.dns = args.dns

        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield ConnectFour()
        yield Footer()


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
