"""
validate_schema.py
Cerebrus validation of game resource configs.
"""

# Third-party python
from cerberus import Validator

# Local modules
from objects import Game
import utils

SHIP_SCHEMA = {
    "name": {"type": "string"},
    "actions": {"type": "list"},
    "formal_name": {"type": "string"},
    "hit_points": {"type": "integer", "min": 1},
    "movement_speed": {"type": "integer", "min": 0},
    "scan_radius": {"type": "integer", "min": 0},
    "nicknames": {"type": "list"},
    "phrase_key": {"type": "string"},
    "rules": {"type": "list"},
    "alliances": {"type": "list"},
}

LOCATION_SCHEMA = {
    "name": {"type": "string"},
    "danger": {"type": "float", "max": 1},
    "alliances": {"type": "list"},
    "rules": {"type": "list"},
    "formal_name": {"type": "string"},
    "phrase_key": {"type": "string"},
}


def validate_ship_configs():
    print("##VALIDATING SHIPS##")
    game = Game(utils.CONFIG)
    resources = game.load_game_resources()
    v = Validator()

    v.schema = SHIP_SCHEMA
    for name, ship in resources["ships"].items():

        if v.validate(ship):
            print(f"Ship {name} passes schema validation")
        else:
            print(name)
            print(v.errors)


def validate_location_configs():
    print("##VALIDATING LOCATIONS##")
    game = Game(utils.CONFIG)
    resources = game.load_game_resources()
    v = Validator()

    v.schema = LOCATION_SCHEMA

    for name, loc in resources["locations"].items():
        if v.validate(loc):
            print(f"Locations {name} passes schema validation")
        else:
            print(name)
            print(v.errors)


if __name__ == "__main__":
    validate_ship_configs()
    validate_location_configs()
