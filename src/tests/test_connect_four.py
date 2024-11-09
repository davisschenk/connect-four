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
        self.assertTrue(all(cell == ConnectCell.EMPTY for col in self.game.board for cell in col))
        self.assertEqual(len(self.game.board[0]), self.game.rows)

    def test_json_conversion(self):
        json = to_json(self.game)

        model = ConnectFour.model_validate_json(json)
        model.board[0][0].emoji()

        self.assertEqual(self.game, model)

    def test_initial_board_empty(self):
        """Test that the board starts with all cells empty."""
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                self.assertEqual(self.game.get_piece(row, col), ConnectCell.EMPTY)

    def test_drop_piece(self):
        """Test dropping a piece into a column."""
        # Drop a red piece into column 3
        self.assertTrue(self.game.drop_piece(3, ConnectCell.RED))
        self.assertEqual(self.game.get_piece(0, 3), ConnectCell.RED)

        # Drop a yellow piece into column 3
        self.assertTrue(self.game.drop_piece(3, ConnectCell.YELLOW))
        self.assertEqual(self.game.get_piece(1, 3), ConnectCell.YELLOW)

        # Drop into a full column should return False
        # Fill up column 3
        for row in range(2, self.game.rows):
            self.game.drop_piece(3, ConnectCell.RED)

        self.assertFalse(self.game.drop_piece(3, ConnectCell.YELLOW))

    def test_check_win_horizontal(self):
        """Test horizontal win condition."""
        # Place red pieces in a horizontal line
        self.game.set_piece(0, 0, ConnectCell.RED)
        self.game.set_piece(0, 1, ConnectCell.RED)
        self.game.set_piece(0, 2, ConnectCell.RED)
        self.game.set_piece(0, 3, ConnectCell.RED)

        winner = self.game.check_win()
        self.assertEqual(winner, ConnectCell.RED)

    def test_check_win_vertical(self):
        """Test vertical win condition."""
        # Place red pieces in a vertical line
        self.game.set_piece(0, 0, ConnectCell.RED)
        self.game.set_piece(1, 0, ConnectCell.RED)
        self.game.set_piece(2, 0, ConnectCell.RED)
        self.game.set_piece(3, 0, ConnectCell.RED)

        winner = self.game.check_win()
        self.assertEqual(winner, ConnectCell.RED)

    def test_check_win_diagonal_down_right(self):
        """Test diagonal down-right win condition."""
        # Place red pieces in a diagonal line (down-right)
        self.game.set_piece(0, 0, ConnectCell.RED)
        self.game.set_piece(1, 1, ConnectCell.RED)
        self.game.set_piece(2, 2, ConnectCell.RED)
        self.game.set_piece(3, 3, ConnectCell.RED)

        winner = self.game.check_win()
        self.assertEqual(winner, ConnectCell.RED)

    def test_check_win_diagonal_up_right(self):
        """Test diagonal up-right win condition."""
        # Place red pieces in a diagonal line (up-right)
        self.game.set_piece(5, 0, ConnectCell.RED)
        self.game.set_piece(4, 1, ConnectCell.RED)
        self.game.set_piece(3, 2, ConnectCell.RED)
        self.game.set_piece(2, 3, ConnectCell.RED)

        winner = self.game.check_win()
        self.assertEqual(winner, ConnectCell.RED)

    def test_no_winner(self):
        """Test that no winner exists in an incomplete game."""
        self.game.set_piece(0, 0, ConnectCell.RED)
        self.game.set_piece(1, 0, ConnectCell.YELLOW)
        winner = self.game.check_win()
        self.assertIsNone(winner)

    def test_invalid_move(self):
        """Test that invalid moves (outside the board) are handled."""
        with self.assertRaises(IndexError):
            self.game.get_piece(6, 0)  # Invalid row index (out of range)

        with self.assertRaises(IndexError):
            self.game.get_piece(0, 7)  # Invalid column index (out of range)

        with self.assertRaises(IndexError):
            self.game.set_piece(6, 0, ConnectCell.RED)  # Invalid row index (out of range)

        with self.assertRaises(IndexError):
            self.game.set_piece(0, 7, ConnectCell.RED)  # Invalid column index (out of range)

    def test_board_display(self):
        """Test that the board can be displayed using rich."""
        try:
            self.game.__rich__()
        except Exception as e:
            self.fail(f"Board display failed with exception: {e}")

    def test_drop_piece_in_full_column(self):
        """Test dropping pieces in a column until full."""
        column = 2
        # Fill the column completely
        for row in range(self.game.rows):
            self.assertTrue(self.game.drop_piece(column, ConnectCell.RED))

        # Attempting to drop in a full column should return False
        self.assertFalse(self.game.drop_piece(column, ConnectCell.YELLOW))
