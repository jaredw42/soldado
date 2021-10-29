# soldado


# intro 
Soldado is a simple Python module for playing a text-based adventure game similar to a "Multi User Dungeon". 

# Requirements
The game itself only requires the `toml` library for parsing configuration and resource files.
It is available using `pip` or `conda` package managers.
`python -m pip install toml`

### Python Version
Soldado requires Python3 and has been tested as far back as Python 3.6. 
### Testing
For unit testing, `pytest` is used.
### Schema Validation 
`Cerberus` is used to validate resource and config files according to the defined schema. 



# Playing
## Starting the game
To start a new game, run the `play_game` python script. The configuration files will load automatically.

`python ./src/play_game.py`

Instructions currently are only available at the start of the game.

## Playing the game
After starting and the instruction prompt, the user will be asked for an action.
Available player actions are `["movements", "sensors", "launch_fighter", "self_destruct"]`.

Inputs can be made in natural language, the game will parse the input and attempt to understand the intention.

Many actions have multiple keywords or phrases to execute them.
For instance, the `movements` action can be initiated with words such as `move`, `movement`,or `movements`, and even context-relevant terms such as `FTL Jump` or `Jump the Ship`.

## Ending the game.
Unfortunately, the game is not winnable in the current state. To end the game, the user must `self destruct`. 
