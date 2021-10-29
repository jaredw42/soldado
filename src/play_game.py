"""
play_game.py
Script that contains the entry point of Games
Keeps track of the game's state and takes user inputs

"""
# system python
import random

# third-party python

# local packages
from enums import GameState, PhraseType
from objects import Game
import utils


PHRASES = utils.PHRASES
CONFIG = utils.CONFIG


def start_new_game(config: dict) -> Game:

    utils.print_output(PHRASES[PhraseType.SPECIAL.value]["new_game_start"])
    game = Game(config)
    return game


def play_game() -> None:

    inp = utils.user_input_prompt(PHRASES[PhraseType.SPECIAL.value]["new_game_prompt"])
    if utils.check_for_affirmative(inp):
        game = start_new_game(CONFIG)
        inp = utils.user_input_prompt(
            random.choice(PHRASES[PhraseType.SPECIAL.value]["game_ready"]).format(
                game.board.player.formal_name
            )
        )
        if utils.check_for_affirmative(inp):
            utils.print_output(
                random.choice(PHRASES[PhraseType.SPECIAL.value]["instructions"]).format(
                    game.board.player.allowed_actions
                )
            )
        game.gamestate = GameState.RUNNING

        successful_last_action = False
        while game.gamestate == GameState.RUNNING:

            # If a player's input did not result in a successful action, do not trigger new events
            if successful_last_action:

                if game.board.player.hit_points <= 0:
                    game.gamestate = GameState.GAME_OVER_PLAYER_DESTROYED
                    break

                # Check what other objects are in the same location as the player's object
                occupants = game.board.occupied_squares[game.board.player.coordinates]
                # shared_occupants will always contain at least the player
                if len(occupants) > 1:
                    for occupant in occupants:
                        if occupant.phrase_key != "player":
                            out = random.choice(
                                PHRASES[PhraseType.DISCOVERY.value][occupant.phrase_key]
                            ).format(occupant.formal_name)
                            utils.print_output(out)

                game.logger.debug("If there was a combat module it would go here.")
                successful_last_action = False

            prompt = random.choice(PHRASES[PhraseType.USER_PROMPT.value]["default_prompt"])
            inp = utils.user_input_prompt(prompt)

            action = utils.check_for_action(inp)

            if not action:
                out = random.choice(
                    PHRASES[PhraseType.COMMAND_REPLY.value]["command_parse_fail"]
                )
                utils.print_output(out.format(inp))
            else:
                out = random.choice(
                    PHRASES[PhraseType.COMMAND_REPLY.value]["command_parse_success"]
                )
                utils.print_output(out.format(inp))

                action_success = game.board.execute_action(action)

                if action_success:
                    successful_last_action = True
                    out = random.choice(
                        PHRASES[PhraseType.ACTION_REPLY.value]["action_success"]
                    )

                else:
                    out = random.choice(
                        PHRASES[PhraseType.ACTION_REPLY.value]["action_failure"]
                    )
                utils.print_output(out.format(game.board.player.formal_name, action.name))

        if game.gamestate == GameState.GAME_OVER_PLAYER_DESTROYED:
            utils.print_output(
                random.choice(
                    PHRASES[PhraseType.GAME_OVER.value]["game_over_player_destroyed"]
                ).format(game.board.player.formal_name)
            )

        elif game.gamestate == GameState.GAME_OVER_OBJECTIVE_DESTROYED:
            utils.print_output(
                PHRASES[PhraseType.GAME_OVER.value]["game_over_objective_destroyed"]
            )

        elif game.gamestate == GameState.GAME_OVER_VICTORY:
            utils.print_output(PHRASES[PhraseType.GAME_OVER.value]["game_over_victory"])


if __name__ == "__main__":
    play_game()
