"""
objects.py

Module containing the objects for playing the game.
There are three base classes: Game, GameBoard and GameObject.

Game is a container that holds the GameBoard, information about the game's state, and the resources for the game.

GameBoard is a container with all the game's objects and the methods to interact with the environment.

GameObject is the base class of all objects in the game
Derived GameObjects: Ship, Location  

"""

# Python standard library
import logging
import random
from pathlib import Path
from typing import Any, MutableMapping, Optional

# Third-party modules
import toml

# Local modules
from enums import Actions, PhraseType
import utils


RESOURCE_PATHS = utils.RESOURCE_PATHS
PHRASES = utils.PHRASES


class Game(object):
    """
    Container to hold a game instance and all associated objects
    """

    def __init__(self, config: dict):
        self.config: dict = config
        self.resource_paths: MutableMapping[str, Any] = RESOURCE_PATHS
        self.resources: dict = self.load_game_resources()
        self.board = GameBoard(
            config["game_board"]["x_len"], config["game_board"]["y_len"]
        )
        self.create_start_locations()
        self.create_start_ships()
        self.gamestate = "RUNNING"
        self.logger = logging.getLogger("Game")
        self.logger.info(f"Game {id(self)} initialized.")

    def create_start_ships(self) -> None:
        """
        Instantiate Ship objects based on config file and add them to the board in random, unoccupied squares.
        """

        for ship, num in self.config["start_conditions"]["ships"].items():
            config = self.resources["ships"][ship]

            for _ in range(0, num):
                newship = Ship(
                    name=config["name"],
                    formal_name=config["formal_name"],
                    phrase_key=config["phrase_key"],
                    rules=config["rules"],
                    alliances=config["alliances"],
                    nicknames=config["nicknames"],
                    movement_speed=config["movement_speed"],
                    scan_radius=config["scan_radius"],
                    hit_points=config["hit_points"],
                    actions=config["actions"],
                )
                self.board.add_ship_to_board(newship)

                if ship == "player":
                    # we will use this a lot, lets make it easy and give it a reference in the game board too.
                    self.board.player = newship
        

    def create_start_locations(self) -> None:
        """
        Instantiate Location objects based on config file and add them to the board in random, unoccupied squares.
        """

        for location, num in self.config["start_conditions"]["locations"].items():

            config = self.resources["locations"][location]
            for _ in range(0, num):
                loc = Location(**config)
                self.board.add_location_to_board(loc)

    def load_game_resources(self) -> dict:
        resources = {}
        for key, val in self.resource_paths["game_objects"].items():
            resource_list = toml.load(Path(utils.PARENT_DIRECTORY, val))[key]
            r_ = {}
            for resource in resource_list:
                for k, v in resource.items():
                    r_[k] = v
            resources[key] = r_

        return resources


class GameBoard(object):
    """
    Container holding all playing objects of game and their associated locations
    Since this object knows where everything is, it also contains the methods
    to move the objects around and introspect the environment
    """

    def __init__(self, x_length: int = 5, y_length: int = 5):

        self.rows = y_length
        self.columns = x_length
        self.total_squares = (self.rows + 1) * (self.columns + 1)
        self.occupied_squares = {}
        self.logger = logging.getLogger("GameBoard")
        self.player = None

    def get_random_unoccupied_square(self) -> tuple:
        """
        convenience function for finding new unoccupied square on GameBoard
        """
        # raise exception if all squares are occupied
        if len(self.occupied_squares.keys()) == self.total_squares:
            raise RuntimeError(
                "Attempted to get random unoccupied square, but all board squares are occupied."
            )
        # Number of columns is the width of X and number of rows is the height of Y
        coords = (random.randint(0, self.columns), random.randint(0, self.rows))

        while coords in self.occupied_squares.keys():
            coords = (random.randint(0, self.columns), random.randint(0, self.rows))

        return coords

    def add_ship_to_board(self, ship: "Ship", coordinates=()) -> None:
        """
        convenience function to add Ship object to board
        """

        if not coordinates:
            coordinates = self.get_random_unoccupied_square()

        if coordinates in self.occupied_squares:
            raise ValueError("Attempted to add ship to occupied GameBoard square")

        ship.coordinates = coordinates
        self.occupied_squares[coordinates] = [ship]
        self.logger.info(f"Ship {ship.name} added to board at {coordinates}")

    def add_location_to_board(self, location: "Location", coordinates=()) -> None:
        """
        convenience function to add Location object to GameBoard
        """

        if not coordinates:
            coordinates = self.get_random_unoccupied_square()

        if coordinates in self.occupied_squares:
            raise ValueError("Attempted to add location to occupied GameBoard square")

        location.coordinates = coordinates
        self.occupied_squares[coordinates] = [location]
        self.logger.info(
            f"Location {location.name} added to board at position {coordinates}."
        )

    def calculate_updated_location_and_validate(
        self, coordinates: tuple, movement: tuple
    ) -> Optional[tuple]:
        """
        Given a set of coordinates and a movement,
        calculate the new coordinates and verify the coordinates are on the board.
        """
        speed = movement[1]
        direction = movement[0].value
        vector = (direction[0] * speed, direction[1] * speed)
        new_location = tuple(map(lambda loc, vec: loc + vec, coordinates, vector))

        negative_coords = [x for x in new_location if x < 0]
        if negative_coords:
            self.logger.info(
                f"Movement from {coordinates} to {new_location} failed negative coordinate validation check"
            )
            return None

        if new_location[0] > self.columns or new_location[1] > self.rows:
            self.logger.info(
                f"Movement from {coordinates} to {new_location} out of board range"
            )
            return None

        self.logger.info(
            f"Movement from {coordinates} to {new_location} passes validation check"
        )
        return new_location

    def move_object(self, object_: "GameObject", new_location: tuple) -> None:
        """
        Moves an object and updates the occupied squares dict
        """

        # Find all objects in the square that are NOT the object we are about to move.
        current_square_objects = self.occupied_squares[object_.coordinates]
        remaining_square_objects = [
            obj for obj in current_square_objects if id(obj) != id(object_)
        ]

        # if there is anything left in the square, update the dict.  Otherwise delete the key
        if remaining_square_objects:
            self.occupied_squares[object_.coordinates] = remaining_square_objects
        else:
            self.logger.info(f"square{object_.coordinates} unoccupied, deleting key.")
            del self.occupied_squares[object_.coordinates]

        if new_location in self.occupied_squares.keys():
            self.occupied_squares[new_location].append(object_)
        else:
            self.occupied_squares[new_location] = [object_]

        object_.coordinates = new_location
        self.logger.info(f"Moved {object_.formal_name} to {object_.coordinates}")

    def execute_action(self, action) -> bool:
        """
        Execute action for an object on the board. 
        """
        if action.value not in self.player.allowed_actions:
            self.logger.debug(
                f"{action.value} not in {self.player.name} action list.\n available actions:{self.actions}"
            )
            return False

        if action == Actions.SENSORS:
            self.player.scan(self.occupied_squares)
        elif action == Actions.MOVE:
            requested_movement = utils.ask_user_how_to_move(self.player)
            movement = self.calculate_updated_location_and_validate(
                self.player.coordinates, requested_movement
            )
            if not movement:
                out = random.choice(
                    PHRASES[PhraseType.ACTION_REPLY.value]["movement_failure"]
                ).format(
                    requested_movement[0].name,
                    requested_movement[1],
                    self.player.coordinates,
                )
                utils.print_output(out)
                return False
            self.move_object(self.player, movement)
            out = random.choice(
                PHRASES[PhraseType.ACTION_REPLY.value]["movement_success"]
            ).format(self.player.formal_name, self.player.coordinates)
            utils.print_output(out)
        elif action == Actions.SELF_DESTRUCT:
            self.player.self_destruct()

        return True


class GameObject(object):
    """
    Base class of objects that will be placed on the board
    """

    def __init__(
        self,
        coordinates: tuple = (0, 0),
        phrase_key: str = "",
        name: str = "",
        formal_name: str = "",
        rules: tuple = (),
    ):
        self.coordinates = coordinates
        self.phrase_key = phrase_key
        self.name = name
        self.formal_name = formal_name


class Ship(GameObject):
    """
    Ship objects, whether they be friend, foe or the player.
    All of them move, most can scan. Some can even shoot.
    Ships don't like their hit points being below zero.
    """

    def __init__(
        self,
        hit_points: int = 1,
        scan_radius: int = 0,
        movement_speed: int = 0,
        name: str = "",
        formal_name: str = "",
        actions: tuple = (),
        phrase_key: str = "",
        rules: tuple = (),
        alliances: tuple = (),
        nicknames: tuple = (),
    ):
        self.hit_points = hit_points
        self.allowed_actions = actions
        self.scan_radius = scan_radius
        self.movement_speed = movement_speed
        self.alliances = alliances
        self.nicknames = nicknames

        super().__init__(
            self, name=name, formal_name=formal_name, phrase_key=phrase_key, rules=rules
        )

        self.logger = logging.getLogger(f"Ship - {self.formal_name}")

    def scan(self, occupied_sectors: dict) -> None:
        """
        Print information about nearby objects.
        """
        def _get_scannable_sectors(location: tuple, radius: int) -> set:

            """
            Return a set of all coordinates in the scan radius of the ship.
            Makes no attempt to determine if they are on the board.
            """

            xcoord = location[0]
            ycoord = location[1]

            scannable_sectors = set()

            for x in range((xcoord - radius), (xcoord + radius + 1)):
                for y in range((ycoord - radius), (ycoord + radius + 1)):
                    scannable_sectors.add((x, y))

            return scannable_sectors

        def _get_distance_between_squares(loc1: tuple, loc2: tuple) -> int:
            """
            Find distance between two squares on board.
            """

            d1 = abs(loc1[0] - loc2[0])
            d2 = abs(loc1[1] - loc2[1])

            return max(d1, d2)

        scannable_sectors = _get_scannable_sectors(self.coordinates, self.scan_radius)
        occupied_coordinates = set(occupied_sectors.keys())
        scanned = scannable_sectors.intersection(occupied_coordinates)
        for sq in scanned:
            objects = occupied_sectors[sq]
            for obj in objects:
                pk = obj.phrase_key
                distance = _get_distance_between_squares(self.coordinates, sq)
                if pk != "player":
                    out = random.choice(PHRASES["detection"][pk])
                    out = out + " This object is {} sectors from here.".format(distance)
                    utils.print_output(out.format(obj.formal_name))

        return None

    def self_destruct(self) -> None:
        """
        Destroys the ship.  If this is the player this ends the game.
        """

        utils.print_output(
            random.choice(PHRASES[PhraseType.ACTION_REPLY.value]["self_destruct_start"])
        )
        self_destruct_confirm = PHRASES[PhraseType.SPECIAL.value]["self_destruct_confirm"]
        self_destruct_abort = PHRASES[PhraseType.SPECIAL.value]["self_destruct_abort"]
        prompt = random.choice(
            PHRASES[PhraseType.USER_PROMPT.value]["self_destruct_confirmation"]
        )
        prompt = prompt.format(self_destruct_confirm, self_destruct_abort)

        final_confirmation = False
        while not final_confirmation:
            response = utils.user_input_prompt(prompt)
            if response == self_destruct_abort:
                utils.print_output(
                    PHRASES[PhraseType.COMMAND_REPLY.value]["self_destruct_abort"]
                )
                final_confirmation = True
            elif response == self_destruct_confirm:
                utils.print_output(
                    PHRASES[PhraseType.COMMAND_REPLY.value]["self_destruct_confirm"]
                )
                self.hit_points = -1
                final_confirmation = True
            else:
                utils.print_output(
                    PHRASES[PhraseType.COMMAND_REPLY.value]["self_destruct_fail"]
                )

        return None


class Location(GameObject):
    """
    A location in space, such as a planet, black hole or nebula
    Locations can be dangerous, which is the probablity the game ends if a player is there.
    """

    def __init__(
        self,
        hit_points: int = 1000,
        danger: int = 0,
        name: str = "",
        formal_name: str = "",
        phrase_key: str = "",
        coordinates: tuple = (0, 0),
        rules: tuple = (),
        alliances: tuple = (),
    ):

        self.hit_points = hit_points
        self.danger = danger
        self.alliances = alliances

        super().__init__(
            self,
            phrase_key=phrase_key,
            name=name,
            formal_name=formal_name,
            rules=rules,
        )
