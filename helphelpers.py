import json
import discord

_HELPERS_PATH = 'json/helpers.json'
_HELPEES_PATH = 'json/helpees.json'


def get_helpers_json() -> dict:
    '''Returns a dictionary of helpers from helpers.json'''
    with open(_HELPERS_PATH, 'r') as f:
        helpers = json.load(f)
    return dict(helpers)


def get_helpees_json() -> dict:
    '''Returns a dictionary of helpees from helpees.json'''
    with open(_HELPEES_PATH, 'r') as f:
        helpees = json.load(f)
    return dict(helpees)


def add_helper(name: str, id: str) -> None:
    '''Adds a helper to helpers.json'''
    helpers = get_helpers_json()
    helpers[id] = name
    with open(_HELPERS_PATH, 'w') as f:
        json.dump(helpers, f, indent=4)


def add_helpee(name: str, id: str) -> None:
    '''Adds a helpee to helpees.json'''
    helpees = get_helpees_json()
    helpees[id] = name
    with open(_HELPEES_PATH, 'w') as f:
        json.dump(helpees, f, indent=4)


def remove_helper(id: str) -> None:
    '''Removes a helper from helpers.json'''
    helpers = get_helpers_json()
    del helpers[id]
    with open(_HELPERS_PATH, 'w') as f:
        json.dump(helpers, f, indent=4)


def remove_helpee(id: str) -> None:
    '''Removes a helpee from helpees.json'''
    helpees = get_helpees_json()
    del helpees[id]
    with open(_HELPEES_PATH, 'w') as f:
        json.dump(helpees, f, indent=4)


def get_helper_name(id: str) -> str:
    '''Returns the helper's name from helpers.json'''
    helpers = get_helpers_json()
    return helpers[id]


def get_helpee_name(id: str) -> str:
    '''Returns the helpee's name from helpees.json'''
    helpees = get_helpees_json()
    return helpees[id]


def make_help_list_embed() -> discord.Embed:
    '''Returns an embed of the helpers and helpees'''
    helpers = get_helpers_json()
    helpees = get_helpees_json()
    embed = discord.Embed(title='Help Availability', color=0xf47fff)
    embed.add_field(name='Helpers', value='\n'.join([id_to_mention(x) for x in helpers.keys()]), inline=False)
    embed.add_field(name='Needs Help', value='\n'.join([id_to_mention(x) for x in helpees.keys()]), inline=False)
    embed.set_footer(text='A bot by yousef :D')
    return embed


def id_to_mention(id: str) -> str:
    '''Returns a mention from an id'''
    return f'<@{id}>'


def clear_helper_list() -> None:
    '''Clears the helper list'''
    with open(_HELPERS_PATH, 'w') as f:
        json.dump({}, f, indent=4)


def clear_helpee_list() -> None:
    '''Clears the helpee list'''
    with open(_HELPEES_PATH, 'w') as f:
        json.dump({}, f, indent=4)
