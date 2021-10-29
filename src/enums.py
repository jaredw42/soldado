"""
enums.py 
Enumerated types 
"""
# Python standard library
from enum import Enum


class GameState(Enum):
    """
    Running states of the game.
    """

    NOT_STARTED = 0
    RUNNING = 1
    GAME_OVER_PLAYER_DESTROYED = 2
    GAME_OVER_OBJECTIVE_DESTROYED = 3
    GAME_OVER_VICTORY = 4


class Actions(Enum):
    """
    Actions available to the player and enemies
    """

    NO_ACTION = "no_action"
    MOVE = "movements"
    SENSORS = "sensors"
    LAUNCH_FIGHTER = "launch_fighter"
    SELF_DESTRUCT = "self_destruct"


class DirectionKeys(Enum):
    """
    Keywords for detecting cardinal direction from player input
    """
    # TODO: move to phrases toml 
    NORTH = ("north", "n", "0")
    NORTHEAST = ("northeast", "ne", "1")
    EAST = ("east", "e", "2")
    SOUTHEAST = ("southeast", "se", "3")
    SOUTH = ("south", "s", "4")
    SOUTHWEST = ("southwest", "sw", "5")
    WEST = ("west", "w", "6")
    NORTHWEST = ("northwest", "nw", "7")


class Directions(Enum):
    """
    Direction names and their mathematical counterparts.
    """

    NORTH = (0, 1)
    NORTHEAST = (1, 1)
    EAST = (1, 0)
    SOUTHEAST = (1, -1)
    SOUTH = (0, -1)
    SOUTHWEST = (-1, -1)
    WEST = (-1, 0)
    NORTHWEST = (-1, 1)


class PhraseType(Enum):
    """
    Keys for the Phrases dictionary.
    """

    DISCOVERY = "discovery"
    DETECTION = "detection"
    SPECIAL = "special"
    USER_INPUT = "user_input"  # inputs from the user (actions, responses, etc.)
    USER_PROMPT = "user_prompt"  # prompts to the user requesting their input
    COMMAND_REPLY = "command_reply"
    ACTION_REPLY = "action_reply"
    GAME_OVER = "game_over"
