import unittest

from lib.connect_four import ConnectCell, ConnectFour
from pydantic_core import to_json


class TestConnectCell(unittest.TestCase):
    def test_emoji(self):
        self.assertEqual(ConnectCell.EMPTY.emoji(), " ")
        self.assertEqual(ConnectCell.RED.emoji(), ":red_circle:")
        self.assertEqual(ConnectCell.YELLOW.emoji(), ":yellow_circle:")


class TestConnectFour(unittest.TestCase):
    def setUp(self):
        self.game = ConnectFour(rows=6, cols=7)

    def test_initialization(self):
        self.assertEqual(self.game.rows, 6)
        self.assertEqual(self.game.cols, 7)
        self.assertTrue(
            all(cell == ConnectCell.EMPTY for col in self.game.board for cell in col),
        )
        self.assertEqual(len(self.game.board[0]), self.game.rows)

    def test_json_conversion(self):
        print(type(ConnectCell.EMPTY))
        json = to_json(self.game)

        model = ConnectFour.model_validate_json(json)
        model.board[0][0].emoji()

        self.assertEqual(self.game, model)
