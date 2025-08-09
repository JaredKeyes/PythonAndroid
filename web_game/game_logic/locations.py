# Refactored location logic for the web game

# Import other logic modules as needed (e.g., combat for forest encounter)
# from . import combat

def get_location_data(location_id, game_state):
    """
    Returns the message and options for a given location ID.
    This acts as a router to the specific location functions.
    """
    if location_id == 'main_camp':
        return main_camp(game_state)
    elif location_id == 'fork':
        return fork(game_state)
    elif location_id == 'left_path': # Renamed from 'left' to avoid conflict with direction
        return left_path(game_state)
    elif location_id == 'right_path': # Renamed from 'right' to avoid conflict with direction
        return right_path(game_state)
    elif location_id == 'forest':
        return forest(game_state)
    elif location_id == 'ocean':
        return ocean(game_state)
    elif location_id == 'mountains':
        return mountains(game_state)
    elif location_id == 'damp_cave': # Added Damp Cave
        return damp_cave(game_state)
    # Add other locations here
    else:
        # Default or error case
        return {
            'message': f"Error: Unknown location '{location_id}'. Returning to camp.",
            'options': main_camp(game_state)['options'], # Provide camp options
            'next_location': 'main_camp'
        }

def main_camp(game_state):
    """Returns data for the main camp."""
    message = ("You are at your main camp.\n\n"
               "To the NORTH, there is a dirt road.\n"
               "To the EAST is a dense forest.\n"
               "Looking SOUTH, you see a vast ocean.\n"
               "Off to the WEST is a large mountain range.\n"
               "You can also stay at the camp and REST.")
    options = [
        {'action': 'go', 'direction': 'north', 'text': 'Go North (Road)'},
        {'action': 'go', 'direction': 'east', 'text': 'Go East (Forest)'},
        {'action': 'go', 'direction': 'south', 'text': 'Go South (Ocean)'},
        {'action': 'go', 'direction': 'west', 'text': 'Go West (Mountains)'},
        {'action': 'rest', 'text': 'Rest at Camp'}
    ]
    return {'message': message, 'options': options}

def fork(game_state):
    """Returns data for the fork in the road."""
    message = "After following the road for a while, you come to a fork."
    options = [
        {'action': 'go', 'direction': 'left', 'text': 'Go Left'},
        {'action': 'go', 'direction': 'right', 'text': 'Go Right'},
        {'action': 'go', 'direction': 'back', 'text': 'Go Back to Camp'} # 'back' implies returning to previous location logic in app.py
    ]
    return {'message': message, 'options': options}

def left_path(game_state):
    """Returns data for the left path."""
    message = ("You went left down the path. The path narrows and you see the dark entrance to a cave, dripping with moisture.")
    options = [
        {'action': 'go', 'direction': 'cave', 'text': 'Enter Damp Cave'}, # Changed direction to 'cave'
        {'action': 'go', 'direction': 'back', 'text': 'Go Back to Fork'}
    ]
    return {'message': message, 'options': options}

def right_path(game_state):
    """Returns data for the right path."""
    message = "You went right down the path. It continues into the distance."
    options = [
        # TODO: Add more options here if the path leads somewhere
        {'action': 'go', 'direction': 'back', 'text': 'Go Back to Fork'}
    ]
    return {'message': message, 'options': options}

def forest(game_state):
    """Returns data for the forest entrance."""
    # Combat encounter logic will be handled in app.py before calling this
    message = ("You arrive at the edge of a dense forest.\n"
               "You can EXPLORE deeper into the woods.\n"
               "Or you can head BACK to camp.")
    options = [
        {'action': 'explore_forest', 'text': 'Explore Forest'},
        {'action': 'go', 'direction': 'back', 'text': 'Go Back to Camp'}
    ]
    return {'message': message, 'options': options}

def ocean(game_state):
    """Returns data for the ocean."""
    message = "You stand at the shore of a vast, sparkling ocean. The waves crash gently."
    options = [
        {'action': 'go', 'direction': 'back', 'text': 'Go Back to Camp'}
    ]
    return {'message': message, 'options': options}

def mountains(game_state):
    """Returns data for the mountains."""
    message = "You arrive at the foothills of a towering mountain range. The peaks disappear into the clouds."
    options = [
        {'action': 'go', 'direction': 'back', 'text': 'Go Back to Camp'}
    ]
    return {'message': message, 'options': options}

from . import items # Import items to check weapon details

def damp_cave(game_state):
    """Returns data for the damp cave."""
    # Combat encounter logic (Slime) will be handled in app.py before calling this
    message = ("You step into the Damp Cave. Water drips constantly from the ceiling, and the air is cool and musty. "
               "Strange, gelatinous shapes seem to quiver in the dim light.")
    options = [
        # TODO: Add exploration options within the cave later?
        {'action': 'go', 'direction': 'back', 'text': 'Leave Cave (Back to Left Path)'}
    ]

    # Check if player already has the sword (equipped or in inventory)
    player_stats = game_state.get('player_stats', {})
    has_sword = ('rusty_sword' in player_stats.get('inventory', [])) or \
                (player_stats.get('equipment', {}).get('weapon') == 'rusty_sword')

    if not has_sword:
        message += "\n\nLying on a damp ledge, you spot a Rusty Sword."
        options.insert(0, {'action': 'take_item', 'item_id': 'rusty_sword', 'text': 'Take Rusty Sword'}) # Add take option

    return {'message': message, 'options': options}

# Add functions for other locations/scenes as needed
