import json
import sys
from dataclasses import dataclass
from enum import Enum
from statistics import mode
from typing import List


class ValueBasedTurn(int, Enum):
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3


DEFAULT_ACTION = ValueBasedTurn.RIGHT


def debug(message: str):
    """ """
    print(
        "turns_until_next_hurdle: {}".format(message),
        file=sys.stderr,
        flush=False,
    )


def output_action(action: ValueBasedTurn = DEFAULT_ACTION):
    debug("output_action: " + action.name)
    print(action.name)


################
# HURDLE GAME
################


@dataclass
class HurdleGameInputs:
    """Generic holder for game inputs"""

    gpu: str
    player_0_pos: int
    player_0_risk: int
    # Below unused
    player_1_pos: int
    player_1_risk: int
    player_2_pos: int
    player_2_risk: int
    unused: int

    def debug_state(self):
        debug(
            json.dumps(
                {
                    "game": "HurdleGameInputs",
                    "gpu": self.gpu,
                    "player_0_pos": self.player_0_pos,
                    "player_0_risk": self.player_0_risk,
                }
            )
        )

    def determine_optimal_action(self):

        self.debug_state()

        if self.player_0_risk > 0:
            return None

        action = ValueBasedTurn.RIGHT

        try:
            turns_until_next_hurdle = self.gpu[self.player_0_pos :].index("#")
            debug(
                "turns_until_next_hurdle: {}".format(turns_until_next_hurdle),
            )

            if not turns_until_next_hurdle or turns_until_next_hurdle > 3:
                action = ValueBasedTurn.RIGHT
            if turns_until_next_hurdle == 3:
                action = ValueBasedTurn.DOWN
            if turns_until_next_hurdle == 2:
                action = ValueBasedTurn.LEFT
            if turns_until_next_hurdle == 1:
                action = ValueBasedTurn.UP

        except Exception as exc:
            debug(exc)  # list index out of range is expected

        debug(
            "HurdleGameInputs._hurdle_determine_optimal_action_for_game: {}".format(action),
        )

        return action


################
# ARCHERY GAME
################


@dataclass
class ArcheryGameInputs:
    """Generic holder for game inputs"""

    # A series of integers, indicating the power of
    # the wind for upcoming turns. The integer
    # at index 0 is the current wind strength.
    gpu: str
    player_0_x: int
    player_0_y: int
    # Below unused
    player_1_x: int
    player_1_y: int
    player_2_x: int
    player_2_y: int
    unused: int

    def debug_state(self):
        debug(
            json.dumps(
                {
                    "game": "ArcheryGameInputs",
                    "gpu": self.gpu,
                    "player_0_x": self.player_0_x,
                    "player_0_y": self.player_0_y,
                }
            )
        )

    def _get_distance_from_center(self):
        return 0 - self.player_0_x, 0 - self.player_0_y

    def determine_optimal_action(self):

        self.debug_state()

        action = ValueBasedTurn.LEFT
        
        try:
            current_wind = int(self.gpu[0])
        except:
            current_wind = 0
        distance_x, distance_y = self._get_distance_from_center()

        debug(f"current_wind: {current_wind}")
        debug(f"x,y: {distance_x}, {distance_y}")

        if abs(distance_x) > abs(distance_y):
            if current_wind - distance_x >= 0:
                action = ValueBasedTurn.LEFT
            else:
                action = ValueBasedTurn.RIGHT

        else:
            if current_wind - distance_y >= 0:
                action = ValueBasedTurn.UP
            else:
                action = ValueBasedTurn.DOWN


        debug(
            "ArcheryGameInputs._hurdle_determine_optimal_action_for_game: {}".format(action),
        )

        return action


################
# SKATING GAME
################


@dataclass
class SkatingGameInputs:
    """Generic holder for game inputs"""

    # This turn's risk order
    gpu: str
    player_0_spaces: int
    player_0_risk: int
    player_1_spaces: int
    player_1_risk: int
    player_2_spaces: int
    player_2_risk: int
    turns_left: int

    def debug_state(self):
        debug(
            json.dumps(
                {
                    "game": "SkatingGameInputs",
                    "gpu": self.gpu,
                    "player_0_spaces": self.player_0_spaces,
                    "player_0_risk": self.player_0_risk,
                }
            )
        )

    def _map_letter_to_action(self, letter: str) -> ValueBasedTurn:
        if letter == "U":
            return ValueBasedTurn.UP
        if letter == "R":
            return ValueBasedTurn.RIGHT
        if letter == "D":
            return ValueBasedTurn.DOWN
        if letter == "L":
            return ValueBasedTurn.LEFT
        return DEFAULT_ACTION

    def _map_gpu_to_actions(self) -> List[ValueBasedTurn]:
        return [self._map_letter_to_action(letter=l) for l in self.gpu]

    def _determine_intersector_risk(self) -> int:

        if (
            self.player_0_spaces % 10 == self.player_1_spaces % 10
            or self.player_0_spaces % 10 == self.player_2_spaces % 10
        ):
            return 2

        return 0

    def determine_optimal_action(self):

        self.debug_state()

        action = ValueBasedTurn.RIGHT

        if self.player_0_risk < 0:
            # stunned, don't care
            return None

        converted_gpu: List[ValueBasedTurn] = self._map_gpu_to_actions()
        risk = self.player_0_risk + self._determine_intersector_risk()

        # if self.player_0_risk >= 5:
        #     # decrease risk
        #     action = converted_gpu[0]

        if risk >= 3:
            # decrease risk
            action = converted_gpu[0]

        else:
            # decrease risk
            action = converted_gpu[3]

        debug(
            "SkatingGameInputs._hurdle_determine_optimal_action_for_game: {}".format(action),
        )

        return action
    

################
# DIVING GAME
################

@dataclass
class DivingGameInputs:
    """Generic holder for game inputs"""

    gpu: str
    player_0_points: int
    player_0_combo: int
    # Below unused
    player_1_points: int
    player_1_combo: int
    player_2_points: int
    player_2_combo: int
    unused: int

    def debug_state(self):
        debug(
            json.dumps(
                {
                    "game": "DivingGameInputs",
                    "gpu": self.gpu,
                    "player_0_pos": self.player_0_points,
                    "player_0_risk": self.player_0_combo,
                }
            )
        )

    def _map_letter_to_action(self, letter: str) -> ValueBasedTurn:
        if letter == "U":
            return ValueBasedTurn.UP
        if letter == "R":
            return ValueBasedTurn.RIGHT
        if letter == "D":
            return ValueBasedTurn.DOWN
        if letter == "L":
            return ValueBasedTurn.LEFT
        return DEFAULT_ACTION

    def determine_optimal_action(self):

        self.debug_state()

        action = self._map_letter_to_action(self.gpu[0])

        debug(
            "DivingGameInputs._hurdle_determine_optimal_action_for_game: {}".format(action),
        )

        return action

################
# GAME LOOPS
################


player_idx = int(input())
nb_games = int(input())
# game loop
while True:
    for i in range(3):
        score_info = input()

    # Store the optimal actions for each "game" in this turn
    optimal_actions = []

    debug(range(nb_games))

    for i in range(nb_games):
        inputs = input().split()

        if i == 0:
            game_inputs = HurdleGameInputs(
                gpu=inputs[0],
                # Player 0
                player_0_pos=int(inputs[1]),
                player_0_risk=int(inputs[4]),
                # Player 1
                player_1_pos=int(inputs[2]),
                player_1_risk=int(inputs[5]),
                # Player 2
                player_2_pos=int(inputs[3]),
                player_2_risk=int(inputs[6]),
                # Unused
                unused=int(inputs[7]),
            )

            optimal_actions.append(game_inputs.determine_optimal_action())

        elif i == 1:

            game_inputs = ArcheryGameInputs(
                gpu=inputs[0],
                # Player 0
                player_0_x=int(inputs[1]),
                player_0_y=int(inputs[2]),
                # Player 1
                player_1_x=int(inputs[3]),
                player_1_y=int(inputs[4]),
                # Player 2
                player_2_x=int(inputs[5]),
                player_2_y=int(inputs[6]),
                # Unused
                unused=int(inputs[7]),
            )

            optimal_actions.append(game_inputs.determine_optimal_action())

        elif i == 2:

            game_inputs = SkatingGameInputs(
                gpu=inputs[0],
                # Player 0
                player_0_spaces=int(inputs[1]),
                player_0_risk=int(inputs[4]),
                # Player 1
                player_1_spaces=int(inputs[2]),
                player_1_risk=int(inputs[5]),
                # Player 2
                player_2_spaces=int(inputs[3]),
                player_2_risk=int(inputs[6]),
                # Unused
                turns_left=int(inputs[7]),
            )

            optimal_actions.append(game_inputs.determine_optimal_action())
        else:
            game_inputs = DivingGameInputs(
                gpu=inputs[0],
                # Player 0
                player_0_points=int(inputs[1]),
                player_0_combo=int(inputs[4]),
                # Player 1
                player_1_points=int(inputs[2]),
                player_1_combo=int(inputs[5]),
                # Player 2
                player_2_points=int(inputs[3]),
                player_2_combo=int(inputs[6]),
                # Unused
                unused=int(inputs[7]),
            )

            optimal_actions.append(game_inputs.determine_optimal_action())
            # debug(str(i))


    # real attempt
    try:

        if False:
            optimal_actions = [x for x in optimal_actions if isinstance(x,ValueBasedTurn)]
            debug("optimal_actions: {}".format(str([oa.name for oa in optimal_actions])))
            output_action(mode(optimal_actions))

        else:
            # output_action(optimal_actions[0])
            # output_action(optimal_actions[1])
            # output_action(optimal_actions[2])
            output_action(optimal_actions[3])
    except:
        output_action(DEFAULT_ACTION)

