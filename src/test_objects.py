"""
test_objects.py
Unit tests for Game and GameObject methods. 
"""
# Python standard library

# Third-party modules
import pytest

# Local modules
from objects import GameBoard, Ship
from enums import Directions


@pytest.fixture(scope="function")
def gameboard() -> GameBoard:
    """
    Fixture for creating an empty GameBoard object with size 2x2
    """
    gameboard = GameBoard(1, 1)

    yield gameboard


@pytest.fixture(scope="session")
def ship() -> Ship:
    """
    Fixture for creating a ship object that can scan and move
    """
    ship = Ship(
        scan_radius=1,
        movement_speed=1,
        actions=("movement", "sensors"),
        formal_name="MCRN Donnager",
        phrase_key="pytest_ship",
    )

    yield ship


def test_move(gameboard: GameBoard, ship: Ship):

    """
    Tests objects get moved and information for both player and board get updated successfully
    """

    gameboard.add_ship_to_board(ship, (0, 0))

    assert ship.coordinates == (0, 0)
    assert (0, 0) in gameboard.occupied_squares.keys()

    gameboard.move_object(ship, (1, 1))
    assert ship.coordinates == (1, 1)
    assert (1, 1) in gameboard.occupied_squares.keys()
    assert (0, 0) not in gameboard.occupied_squares.keys()


# This is kind of gross, but we want a second ship fixture with different names/phrase keys for test_scan.
newship = ship

def test_scan(gameboard: GameBoard, ship: ship, newship: ship, capfd: pytest.fixture):
    """
    Add another ship to the board and run the scan function.
    Check the output matches what is expected.
    """
    newship.formal_name = "USS Reliant"
    newship.phrase_key = "pytest_scan_target"
    print(ship.name)

    gameboard.add_ship_to_board(ship, (0, 0))
    gameboard.add_ship_to_board(newship, (0, 1))

    ship.scan(gameboard.occupied_squares)
    out, err = capfd.readouterr()
    EXPECTED_SCAN_OUTPUT = '\nTarget: USS Reliant detected. This object is 1 sectors from here.\nTarget: MCRN Donnager detected. This object is 0 sectors from here.\n'
    assert out == EXPECTED_SCAN_OUTPUT


def test_calculate_updated_location_and_validate(gameboard: GameBoard):

    """
    Tests movement direction and validation logic.
    """
    direction = Directions.EAST
    location = (0, 0)
    speed = 1

    new_location = gameboard.calculate_updated_location_and_validate(
        location, (direction, speed)
    )

    assert new_location != (0, 1)

    # This is a movement off the board and should return None.
    direction = Directions.WEST
    new_location = gameboard.calculate_updated_location_and_validate(
        location, (direction, speed)
    )
    assert new_location is None


def test_add_ship_to_board(gameboard, ship):

    """
    Tests that randomly adding ships will fill up the board
    Also tests that adding ship to full board or occupied square will fail as expected
    """

    for _ in range(0, 4):
        gameboard.add_ship_to_board(ship)

    # The board should now be fully occupied.
    assert len(gameboard.occupied_squares.keys()) == gameboard.total_squares

    # Adding with no location should fail to get a random square
    with pytest.raises(RuntimeError):
        gameboard.add_ship_to_board(ship)

    with pytest.raises(ValueError):
        gameboard.add_ship_to_board(ship, (0, 0))
