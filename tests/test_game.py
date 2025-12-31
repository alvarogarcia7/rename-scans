import unittest

from app.main import PlayerRepository, UIRepresentation, Game, Player
from unittest.mock import Mock, MagicMock


class TestGame(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.players = PlayerRepository()
        self.game = Game(self.players)

    def test_add_a_player(self) -> None:
        self.players.add = MagicMock()  # type: ignore
        self.players.find_all = MagicMock(return_value=[])  # type: ignore

        self.game.run("add player Pippo")

        self.players.add.assert_called_with(Player('Pippo', 0))

    def test_formatting_of_the_resulting_players(self) -> None:
        self.players.add(Player('Pippo', 0))

        response = self.game.run("add player Pluto")

        self.assertEqual(response, "players: Pippo, Pluto")

    def test_when_there_is_an_exception_when_adding_a_player(self) -> None:
        self.players.add = Mock(side_effect=Exception())  # type: ignore

        response = self.game.run("add player Pippo")

        self.assertEqual(response, "Pippo: already existing player")

    def test_moving_a_player(self) -> None:
        self.players.add(Player('Pippo', 0))
        self.players.add(Player('Pluto', 0))

        response = self.game.run("move Pippo 4, 2")

        self.assertEqual(response, "Pippo rolls 4, 2. Pippo moves from Start to 6")

    def test_moving_another_player(self) -> None:
        self.players.add(Player('Pippo', 0))
        self.players.add(Player('Pluto', 1))

        response = self.game.run("move Pluto 4, 2")

        self.assertEqual(response, "Pluto rolls 4, 2. Pluto moves from 1 to 7")

    def test_winning_the_game(self) -> None:
        self.players.add(Player('Pippo', 60))
        self.players.add(Player('Pluto', 0))

        response = self.game.run("move Pippo 1, 2")

        self.assertEqual(response, "Pippo rolls 1, 2. Pippo moves from 60 to 63. Pippo wins!!")

    def test_bounce_past_the_winning_space(self) -> None:
        self.players.add(Player('Pippo', 60))
        self.players.add(Player('Pluto', 0))

        response = self.game.run("move Pippo 3, 2")

        self.assertEqual(response, "Pippo rolls 3, 2. Pippo moves from 60 to 63. Pippo bounces! Pippo returns to 61")


class TestPlayers(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.players = PlayerRepository()

    def test_add_a_player(self) -> None:
        self.players.add(Player('player_name', 0))

        self.assertEqual(self.players.find_all(), [Player('player_name', 0)])

    def test_add_a_second_player(self) -> None:
        self.players.add(Player('player_name_1', 0))

        self.players.add(Player('player_name_2', 0))

        self.assertEqual(self.players.find_all(), [Player('player_name_1', 0), Player('player_name_2', 0)])

    def test_cannot_add_a_repeated_player(self) -> None:
        self.players.add(Player("Pippo", 0))

        with self.assertRaises(Exception):
            self.players.add(Player("Pippo", 0))


class TestPlayer(unittest.TestCase):
    def test_move_it(self) -> None:
        player = Player('P1', 0)

        player.move(1)

        self.assertEqual(1, player.position)


class TestUIRepresentation(unittest.TestCase):

    def setUp(self) -> None:
        self.ui_representation = UIRepresentation()

    def test_show_position_start(self) -> None:
        self.assertEqual('Start', self.ui_representation.position(0))
