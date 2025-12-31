from __future__ import annotations

import sys
from typing import List, Any, Tuple, cast


def main() -> None:
    game = Game(PlayerRepository())
    while True:
        strip = sys.stdin.readline().strip()
        if not strip:
            break
        output = game.run(strip)
        sys.stdout.write(output + "\n")


if __name__ == '__main__':
    main()


class PlayerRepository:
    names: list[Player]

    def __init__(self) -> None:
        self.names = []

    def add(self, name: Player) -> None:
        if name in self.names:
            raise Exception("Repeated user")

        self.names.append(name)

    def find_all(self) -> List[Player]:
        return self.names

    def find_by_name(self, name: str) -> Player:
        player: Player = list(filter(lambda current: current.name == name, self.names))[0]
        assert player is not None
        return player


class UIRepresentation:
    def position(self, index_of_position: int) -> str:
        result = str(index_of_position)
        if not index_of_position:
            result = 'Start'
        return result

    @staticmethod
    def get_die_values(raw_values: List[str]) -> List[int]:
        return list(map(lambda x: int(x.strip().replace(',', '')), raw_values))


class Game:
    user_names: list[str]

    def __init__(self, players: PlayerRepository) -> None:
        self.players = players
        self.user_names = []
        self.ui_representation = UIRepresentation()

    def run(self, user_input: str) -> str:
        user_input_parts = user_input.split(" ")
        user_name = user_input_parts[-1]
        self.user_names.append(user_name)
        action = user_input_parts[0]
        if action == 'move':
            user_name = user_input_parts[1]
            die_values = self.ui_representation.get_die_values(user_input_parts[-2:])
            user = self.players.find_by_name(user_name)
            return self.compose_moving_message(user, die_values)
        try:
            self.players.add(Player(user_name, 0))
        except Exception:
            return f"{user_name}: already existing player"
        names = list(map(lambda player: player.name, self.players.find_all()))
        return f"players: {', '.join(names)}"

    def compose_moving_message(self, player: Player, die_values: list[int]) -> str:
        previous_position = self.ui_representation.position(player.position)
        sum_of_die = sum(die_values)
        move, bounce = player.move(sum_of_die)
        current_position = self.ui_representation.position(player.position)
        user_name = player.name
        die_values_str = list(map(lambda x: str(x), die_values))
        moving_message = f'{user_name} rolls {", ".join(die_values_str)}. {user_name} moves from {previous_position} to {current_position}'
        if player.position == 63:
            moving_message += f". {user_name} wins!!"
        elif player.position > 63:
            current_position = self.ui_representation.position(63)
            moving_message = f'{user_name} rolls {", ".join(die_values_str)}. {user_name} moves from {previous_position} to {current_position}'
            player.move(2 * (63 - player.position))
            moving_message += f". {user_name} bounces! {user_name} returns to {self.ui_representation.position(player.position)}"
        return moving_message


class Player:
    def __init__(self, name: str, position: int) -> None:
        self.name = name
        self.position = position

    def move(self, spaces: int) -> Tuple[Any, Any]:
        self.position += spaces
        return None, None

    def __eq__(self, o: object) -> bool:
        return o.name == self.name and o.position == self.position  # type: ignore
