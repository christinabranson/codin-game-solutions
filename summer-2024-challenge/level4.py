import json
import sys
from dataclasses import asdict, dataclass
from enum import Enum
from statistics import mode
from typing import List, Union


class ValueBasedTurn(int, Enum):
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3


DEFAULT_ACTION = ValueBasedTurn.RIGHT


def _map_letter_to_action(letter: str) -> ValueBasedTurn:
    if letter == "U":
        return ValueBasedTurn.UP
    if letter == "R":
        return ValueBasedTurn.RIGHT
    if letter == "D":
        return ValueBasedTurn.DOWN
    if letter == "L":
        return ValueBasedTurn.LEFT
    return DEFAULT_ACTION


@dataclass
class GameState:
    game: str
    optimal_action: ValueBasedTurn
    current_score: int = -1
    current_place: int = -1
    remaining_turns: int = -1
    force_priority: bool = False


def parse_game_states_for_priority(
    game_states: List[GameState],
    exclude_games=[]
    #exclude_games=["DIVING"]
) -> Union[None, ValueBasedTurn]:
    force_priority_action = [
        gs.optimal_action
        for gs in game_states
        if gs.force_priority and gs.game not in exclude_games and gs.optimal_action is not None
    ]
    return force_priority_action[0] if len(force_priority_action) else None


def get_mode_of_game_states(game_states: List[GameState]) -> ValueBasedTurn:
    optimal_actions = [gs.optimal_action for gs in game_states if gs.optimal_action is not None]
    return mode(optimal_actions)


def debug(message: str):
    """ """
    print(
        message,
        file=sys.stderr,
        flush=False,
    )


def output_action(action: ValueBasedTurn = DEFAULT_ACTION):
    debug("output_action: " + action.name)
    print(action.name)


@dataclass
class BaseGameInputs:
    game: str
    gpu: str

    @property
    def optimal_action(self) -> Union[None, ValueBasedTurn]:
        return None

    @property
    def remaining_turns(self) -> Union[None, int]:
        if self.gpu == "GAME_OVER":
            return None
        try:
            return len(self.gpu)
        except:
            pass
        return None

    @property
    def current_score(self) -> Union[None, int]:
        return -1  # Not implemented

    @property
    def current_place(self) -> Union[None, int]:
        return -1  # Not implemented

    @property
    def should_force_priority(self) -> bool:
        return False

    @property
    def game_state(self) -> GameState:
        game_state = GameState(
            game=self.game,
            optimal_action=self.optimal_action,
            current_score=self.current_score,
            current_place=self.current_place,
            remaining_turns=self.remaining_turns,
            force_priority=self.should_force_priority,
        )
        debug(
            json.dumps(
                {
                    "game": self.game,
                    "game_state": asdict(game_state),
                },
                default=str,
                indent=2,
            )
        )
        return game_state

    def debug_state(self):
        debug(
            json.dumps(
                asdict(self),
                default=str,
                indent=2,
            )
        )


################
# HURDLE GAME
################


@dataclass
class HurdleGameInputs(BaseGameInputs):
    """Generic holder for game inputs"""

    player_0_pos: int
    player_0_risk: int
    # Below unused
    player_1_pos: int
    player_1_risk: int
    player_2_pos: int
    player_2_risk: int
    unused: int

    @property
    def current_score(self) -> Union[None, int]:
        return self.player_0_pos

    @property
    def current_place(self) -> Union[None, int]:
        if (
            self.player_0_pos >= self.player_1_pos
            and self.player_0_pos >= self.player_2_pos
        ):
            return 1

        if (
            self.player_0_pos >= self.player_1_pos
            or self.player_0_pos >= self.player_2_pos
        ):
            return 2

        return 3

    @property
    def should_force_priority(self) -> bool:
        if self.gpu == "GAME_OVER":
            return False
        return self.current_place == 3

    @property
    def optimal_action(self) -> Union[None, ValueBasedTurn]:

        self.debug_state()

        if self.gpu == "GAME_OVER":
            return None

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
            "HurdleGameInputs._hurdle_determine_optimal_action_for_game: {}".format(
                action
            ),
        )

        return action


################
# ARCHERY GAME
################


@dataclass
class ArcheryGameInputs(BaseGameInputs):
    """Generic holder for game inputs"""

    # A series of integers, indicating the power of
    # the wind for upcoming turns. The integer
    # at index 0 is the current wind strength.
    player_0_x: int
    player_0_y: int
    # Below unused
    player_1_x: int
    player_1_y: int
    player_2_x: int
    player_2_y: int
    unused: int

    @property
    def current_score(self) -> Union[None, int]:
        return self._get_distance_from_center_total(
            x=self.player_0_x,
            y=self.player_0_y,
        )

    @property
    def current_place(self) -> Union[None, int]:
        player_0 = self._get_distance_from_center_total(
            x=self.player_0_x,
            y=self.player_0_y,
        )
        player_1 = self._get_distance_from_center_total(
            x=self.player_1_x,
            y=self.player_1_y,
        )
        player_2 = self._get_distance_from_center_total(
            x=self.player_2_x,
            y=self.player_2_y,
        )

        if player_0 <= player_1 and player_0 <= player_2:
            return 1

        if player_0 <= player_1 or player_0 <= player_2:
            return 2

        return 3

    @property
    def should_force_priority(self) -> bool:
        if self.gpu == "GAME_OVER":
            return False
        return self.current_place == 3

    def _get_distance_from_center(self):
        return 0 - self.player_0_x, 0 - self.player_0_y

    def _get_distance_from_center_total(self, x, y):
        return abs(x) + abs(y)

    @property
    def optimal_action(self) -> Union[None, ValueBasedTurn]:

        self.debug_state()

        if self.gpu == "GAME_OVER":
            return None

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
            "ArcheryGameInputs._hurdle_determine_optimal_action_for_game: {}".format(
                action
            ),
        )

        return action


################
# SKATING GAME
################


@dataclass
class SkatingGameInputs(BaseGameInputs):
    """Generic holder for game inputs"""

    # This turn's risk order
    player_0_spaces: int
    player_0_risk: int
    player_1_spaces: int
    player_1_risk: int
    player_2_spaces: int
    player_2_risk: int
    turns_left: int

    @property
    def current_score(self) -> Union[None, int]:
        return self.player_0_spaces

    @property
    def current_place(self) -> Union[None, int]:
        if (
            self.player_0_spaces >= self.player_1_spaces
            and self.player_0_spaces >= self.player_2_spaces
        ):
            return 1

        if (
            self.player_0_spaces >= self.player_1_spaces
            or self.player_0_spaces >= self.player_2_spaces
        ):
            return 2

        return 3

    @property
    def should_force_priority(self) -> bool:
        if self.gpu == "GAME_OVER":
            return False
        return self.current_place == 3

    def _map_gpu_to_actions(self) -> List[ValueBasedTurn]:
        return [_map_letter_to_action(letter=l) for l in self.gpu]

    def _determine_intersector_risk(self) -> int:

        if (
            self.player_0_spaces % 10 == self.player_1_spaces % 10
            or self.player_0_spaces % 10 == self.player_2_spaces % 10
        ):
            return 2

        return 0

    @property
    def optimal_action(self) -> Union[None, ValueBasedTurn]:

        self.debug_state()

        if self.gpu == "GAME_OVER":
            return None

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
            "SkatingGameInputs._hurdle_determine_optimal_action_for_game: {}".format(
                action
            ),
        )

        return action


################
# DIVING GAME
################


@dataclass
class DivingGameInputs(BaseGameInputs):
    """Generic holder for game inputs"""

    DIVING_PRIORITY = 4

    player_0_points: int
    player_0_combo: int
    # Below unused
    player_1_points: int
    player_1_combo: int
    player_2_points: int
    player_2_combo: int
    unused: int

    @property
    def current_score(self) -> Union[None, int]:
        return self.player_0_points

    @property
    def current_place(self) -> Union[None, int]:
        if (
            self.player_0_points >= self.player_1_points
            and self.player_0_points >= self.player_2_points
        ):
            return 1

        if (
            self.player_0_points >= self.player_1_points
            or self.player_0_points >= self.player_2_points
        ):
            return 2

        return 3

    @property
    def should_force_priority(self) -> bool:
        if self.gpu == "GAME_OVER":
            return False
        # if self.remaining_turns >=15: # first 2 turns skip diving
        #     return False

        if self.player_0_combo <= self.player_1_combo:
            return True

        if self.player_0_combo <= self.player_2_combo:
            return True

        if self.player_0_points <= self.player_1_points:
            return True

        if self.player_0_points <= self.player_2_points:
            return True

        return (
            self.remaining_turns <= self.DIVING_PRIORITY  # make sure to end on combos
            or self.current_place == 3  # prioritize if losing
        )

    @property
    def optimal_action(self) -> Union[None, ValueBasedTurn]:

        self.debug_state()

        if self.gpu == "GAME_OVER":
            return None

        action = _map_letter_to_action(self.gpu[0])

        debug(
            "DivingGameInputs._hurdle_determine_optimal_action_for_game: {}".format(
                action
            ),
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
    game_states: List[GameState] = []

    for i in range(nb_games):
        inputs = input().split()

        if i == 0:
            game_inputs = HurdleGameInputs(
                game="HURDLE",
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

        elif i == 1:

            game_inputs = ArcheryGameInputs(
                game="ARCHERY",
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

        elif i == 2:

            game_inputs = SkatingGameInputs(
                game="SKATING",
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

        else:
            game_inputs = DivingGameInputs(
                game="DIVING",
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

        game_states.append(game_inputs.game_state)

    try:
        # If diving game is forcing priority, do that
        # if game_states[3].force_priority:
        #     debug("Diving game is priority, using that action...")
        #     output_action(game_states[3].optimal_action)
        if parse_game_states_for_priority(game_states):
            debug("Another game has a forced priority, so using that...")
            output_action(parse_game_states_for_priority(game_states))
        else:
            debug("Just using the mode...")
            the_mode = get_mode_of_game_states(game_states)
            output_action(the_mode)

    except Exception as e:
        debug(e)
        output_action(DEFAULT_ACTION)
