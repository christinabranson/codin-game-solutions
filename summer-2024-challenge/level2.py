"""
Functionality to navigate level 2 of https://www.codingame.com/ide/challenge/summer-challenge-2024-olymbits

General methodology is:
- Loop through all "turns"
- Loop through all 4 "games" for a single turn
"""

import sys
from enum import Enum
from statistics import mode
from typing import List


class ValueBasedTurn(int, Enum):
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3


DEFAULT_ACTION = ValueBasedTurn.RIGHT


player_idx = int(input())
nb_games = int(input())
print("nb_games: {}".format(str(nb_games)), file=sys.stderr, flush=False)


def _hurdle_determine_optimal_action_for_game(gpu, location) -> ValueBasedTurn:
    """
    Based on the map state & the location of the player, determine
    the best move available for this game

    This is a function of the number of turns until the next hurdle

    Note: KeyErrors/ValueErrors are expected as we're "looking ahead" based
    on the current position and we're expecting to "fall off" the map
    """
    print("gpu: {} | location: {}".format(gpu, location), file=sys.stderr, flush=False)

    turns_until_next_hurdle = gpu[location:].index("#")
    print(
        "turns_until_next_hurdle: {}".format(turns_until_next_hurdle),
        file=sys.stderr,
        flush=False,
    )

    action = DEFAULT_ACTION
    if not turns_until_next_hurdle or turns_until_next_hurdle > 3:
        action = ValueBasedTurn.RIGHT
    if turns_until_next_hurdle == 3:
        action = ValueBasedTurn.DOWN
    if turns_until_next_hurdle == 2:
        action = ValueBasedTurn.LEFT
    if turns_until_next_hurdle == 1:
        action = ValueBasedTurn.UP

    print(
        "_hurdle_determine_optimal_action_for_game: {}".format(action),
        file=sys.stderr,
        flush=False,
    )

    return action


def _hurdle_determine_optimal_actions_across_all_games(
    optimal_actions: List[ValueBasedTurn],
) -> ValueBasedTurn:
    """
    Look across all optimal actions and make decision based on the
    following logic
    """
    # If at least one game should UP (jump), do it
    if ValueBasedTurn.UP in optimal_actions:
        return ValueBasedTurn.UP
    else:
        # Otherwise, determine the most common optimal action (excluding UP)
        optimal_actions_sans_up = list(
            filter(lambda a: a != ValueBasedTurn.UP, optimal_actions)
        )
        print(
            "optimal_actions_sans_up: {}".format(str(optimal_actions_sans_up)),
            file=sys.stderr,
            flush=False,
        )
        return mode(optimal_actions_sans_up)


# game loop
while True:
    for i in range(3):
        score_info = input()

    # Store the optimal actions for each "game" in this turn
    optimal_actions = []

    for i in range(nb_games):
        inputs = input().split()
        # ASCII representation of the racetrack. . for empty space. # for hurdle
        gpu = inputs[0]
        # position of player 1
        reg_0 = int(inputs[1])
        reg_1 = int(inputs[2])  # unused right now
        reg_2 = int(inputs[3])  # unused right now
        # stun timer for player 1
        reg_3 = int(inputs[4])
        reg_4 = int(inputs[5])  # unused right now
        reg_5 = int(inputs[6])  # unused right now
        reg_6 = int(inputs[7])  # unused right now

        # only care about the optimal action if we're not stunned
        if reg_3 == 0:
            action = DEFAULT_ACTION
            try:
                action = _hurdle_determine_optimal_action_for_game(gpu, reg_0)
            except Exception as e:
                # KeyErrors/ValueErrors expected as we're "looking ahead"
                # in the map
                print(e, file=sys.stderr, flush=False)

            # Store the optimal action for this game
            optimal_actions.append(action)

    print(
        "optimal_actions: {}".format(str(optimal_actions)), file=sys.stderr, flush=False
    )

    print(
        _hurdle_determine_optimal_actions_across_all_games(
            optimal_actions=optimal_actions
        ).name
    )
