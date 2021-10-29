"""
utils.py
Module containing links to game resources and utility methods for the game.

"""
# Python standard library
import logging
from pathlib import Path
import random
from typing import Iterable, Type, Union

#third-party Python
import toml

# Local modules
from enums import Actions, DirectionKeys, Directions, PhraseType

PARENT_DIRECTORY = Path(__file__).parent.resolve()
RESOURCE_PATH_FILE = Path(PARENT_DIRECTORY, "resource_paths.toml")
RESOURCE_PATHS = toml.load(RESOURCE_PATH_FILE)
PHRASE_PATH = Path(PARENT_DIRECTORY, RESOURCE_PATHS["phrases"]["phrases_english"])
PHRASES = toml.load(PHRASE_PATH)["phrases"][0]

CONFIGPATH = Path(PARENT_DIRECTORY, RESOURCE_PATHS["configs"]["config"])
CONFIG = toml.load(CONFIGPATH)["config"]


LOG_LEVEL = logging.WARNING
logging.basicConfig(level=LOG_LEVEL, format="%(name)s - %(message)s")
LOGGER = logging.getLogger("Utils")


def check_for_affirmative(input_string: str) -> bool:

    """
    parses string and checks for words indicating the user means "YES"
    """

    # if input is exactly one of these,
    exact_matches = PHRASES["user_input"]["exact_affirmatives"]

    affirmative = False
    check_string = input_string.lower()
    for match in exact_matches:
        if check_string == match:
            affirmative = True
            break

    if not affirmative:
        # TODO: make this a regex or be smarter about this
        split_matches = PHRASES[PhraseType.USER_INPUT.value]["sentance_contains_affirmatives"]
        split_check = check_string.split()
        for word in split_check:
            for match in split_matches:
                if word == match:
                    affirmative = True
                    break

    return affirmative


def check_for_negative(input_string: str) -> bool:
    """
    parses string and checks for words indicating the user means "NO"
    """

    # if input is exactly one of these,
    exact_matches = PHRASES[PhraseType.USER_INPUT.value]["exact_negatives"]

    affirmative = False
    check_string = input_string.lower()
    for match in exact_matches:
        if check_string == match:
            affirmative = True
            break

    if not affirmative:
        # TODO: make this a regex or be smarter about this
        split_matches = PHRASES["user_input"]["sentance_contains_negatives"]
        split_check = check_string.split()
        for word in split_check:
            for match in split_matches:
                if word == match:
                    affirmative = True
                    break

    return affirmative



def print_output(output: Union[str, list]) -> None:
    """
    Prints output from a list or string.  Adds newline characters when missing
    """
    if type(output) == list:
        i = random.randint(0, len(output) - 1)
        output = output[i]

    if not output.endswith("\n"):  # type: ignore
        output += "\n"

    print(output)


def user_input_prompt(prompts: Union[str, list], input_line_prompt: str = "-> ") -> str:

    """
    convenience function for displaying user input prompt
    """
    if type(prompts) == list:
        i = random.randint(0, len(prompts) - 1)
        input_string = prompts[i]
    else:
        input_string = prompts
    if not input_string.endswith("\n"):  # type: ignore
        input_string += "\n"

    input_string += input_line_prompt

    if not input_string.endswith(" "):
        input_string += " " # type: ignore

    return input(input_string)


def check_for_keywords(input_string: str, action_keywords: Iterable[str] = []) -> bool:

    """
    Parse string and check to see if it contains a word from a list
    """

    LOGGER.info(
        f"checking {input_string} for action_keywords {' '.join(action_keywords)}"
    )
    found = False
    # check for exact match
    exact = [x for x in action_keywords if x == input_string.lower()]

    if exact:
        LOGGER.info(f"Exact keyword match found for user input {input_string}")
        found = True
    else:
        sentence = input_string.split(" ")
        for word in sentence:
            for kw in action_keywords:
                if word.lower() == kw:
                    LOGGER.info(f"keyword match. {kw}")
                    return True
    return found


def check_for_action(input_string: str) -> Union[Actions, None]:
    """
    Check an input string for action keywords
    """
    for ac in Actions:
        keywords = PHRASES["action_keywords"][ac.value]
        if check_for_keywords(input_string, keywords):
            return ac
    return None

def ask_user_how_to_move(user: Type['Ship']) -> tuple:
    """
    If the user selects the movement action, prompt for direction and distance inputs.
    """
    direction = None
    while not direction:

        response = user_input_prompt(
            random.choice(
                PHRASES[PhraseType.USER_PROMPT.value]["movement_direction_query"]
            ).format(user.formal_name, user.coordinates)
        )

        for dk in DirectionKeys:
            if check_for_keywords(response, dk.value):
                print_output(
                    random.choice(
                        PHRASES[PhraseType.COMMAND_REPLY.value]["direction_parse_success"]
                    ).format(dk.name)
                )
                direction = Directions[dk.name]
                break
        if not direction:
            print_output(
                random.choice(
                    PHRASES[PhraseType.COMMAND_REPLY.value]["direction_parse_fail"]
                ).format(response)
            )

    distance = None
    while not distance:
        response = user_input_prompt(
            random.choice(
                PHRASES[PhraseType.USER_PROMPT.value]["movement_speed_query"]
            ).format(user.movement_speed)
        )

        try:
            input_distance = int(response)
            if 0 <= input_distance <= user.movement_speed:
                print_output(
                    random.choice(
                        PHRASES[PhraseType.COMMAND_REPLY.value]["speed_parse_success"]
                    ).format(input_distance)
                )
                distance = input_distance
                return (direction, distance)
        except ValueError as e:
            print_output(
                random.choice(
                    PHRASES[PhraseType.COMMAND_REPLY.value]["speed_parse_fail"]
                ).format(response)
            )
