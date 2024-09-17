from lib.connect_four import ConnectCell, ConnectFour
import unittest


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
            all(cell == ConnectCell.EMPTY for row in self.game.board for cell in row)
        )
        self.assertEqual(len(self.game.board), self.game.rows)
        self.assertEqual(len(self.game.board[0]), self.game.cols)

    def test_pack_unpack(self):
        # Set up the board with a specific pattern
        self.game.board[0][0] = ConnectCell.RED
        self.game.board[1][1] = ConnectCell.YELLOW
        self.game.board[2][2] = ConnectCell.RED

        # Pack the current state
        packed_value = self.game.pack()

        # Unpack into a new game instance
        new_game = ConnectFour.unpack(packed_value)

        # Test that the new game instance has the same properties
        self.assertEqual(new_game.rows, self.game.rows)
        self.assertEqual(new_game.cols, self.game.cols)
        self.assertEqual(new_game.board[0][0], ConnectCell.RED)
        self.assertEqual(new_game.board[1][1], ConnectCell.YELLOW)
        self.assertEqual(new_game.board[2][2], ConnectCell.RED)

    def test_pack_unpack_empty_board(self):
        # Pack the initial empty state
        packed_value = self.game.pack()

        # Unpack into a new game instance
        new_game = ConnectFour.unpack(packed_value)

        # Test that the new game instance has the same properties
        self.assertEqual(new_game.rows, self.game.rows)
        self.assertEqual(new_game.cols, self.game.cols)
        self.assertTrue(
            all(cell == ConnectCell.EMPTY for row in new_game.board for cell in row)
        )
