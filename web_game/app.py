from flask import Flask, render_template, request, jsonify, session
import secrets
import os
import random # For forest encounter chance
import math # Needed for level up calculation

# Import game logic modules
from game_logic import locations, combat, items # Import items module
# Character creation logic will be handled directly here for simplicity,
# or could be moved to its own module later.

app = Flask(__name__)
# Generate a secret key for session management
# In a real application, use environment variables or a config file
app.secret_key = secrets.token_hex(16)

# --- Helper Functions ---
def calculate_xp_for_next_level(level):
    """Calculates the XP needed for the next level based on the formula."""
    # Halved the base requirement from 100 to 50 and reduced exponent from 1.5 to 1.3
    return math.ceil(50 * (level ** 1.3)) # Use ceil to ensure integer XP requirement

@app.route('/')
def index():
    """Renders the main game page."""
    # Initialize session if not already done
    if 'game_state' not in session:
        session['game_state'] = {
            'current_location': 'character_creation', # Start with character creation
            'player_stats': None, # Will store {'name': '...', 'health': ..., ...}
            'message': "Welcome! Let's create your character.",
            'options': [],
            'combat_state': None, # Will store combat details if active
            'previous_location': None # To handle 'back' actions
        }
        # Start character creation - for now, just ask for name
        session['game_state']['message'] = "Welcome, adventurer! What is your name?"
        session['game_state']['options'] = [{'action': 'submit_name', 'text': 'Confirm Name', 'input_required': 'text'}] # Indicate input needed

    # Ensure player_stats is updated in the template context if it exists in session
    game_state_for_template = session.get('game_state', {})
    combat_state = game_state_for_template.get('combat_state') # Get combat_state safely

    # Check if combat_state is a dictionary and 'player' key exists
    if isinstance(combat_state, dict) and 'player' in combat_state:
        # If in combat (or just finished), update player stats from combat state for display
        game_state_for_template['player_stats'] = combat_state['player']
    # No need for the elif, as the above check covers the case where combat_state is a dict.
    # If combat_state is None or not a dict, player_stats remains as it was from the main game_state.

    return render_template('index.html', game_state=game_state_for_template)

@app.route('/action', methods=['POST'])
def handle_action():
    """Handles player actions sent from the frontend."""
    data = request.get_json()
    action = data.get('action')
    player_input = data.get('input', None) # For text input like name
    direction = data.get('direction', None) # For 'go' actions

    game_state = session.get('game_state', {})
    current_location = game_state.get('current_location')
    combat_active = game_state.get('combat_state') is not None and not game_state['combat_state'].get('is_over', False)

    # --- Game Logic Integration ---

    if combat_active:
        # Handle combat actions
        if action in ['combat_attack', 'combat_defend']:
            combat_action = action.split('_')[1] # Get 'attack' or 'defend'
            game_state['combat_state'] = combat.handle_combat_action(game_state['combat_state'], combat_action)
            game_state['message'] = game_state['combat_state']['turn_message']
            game_state['options'] = combat.get_combat_options(game_state['combat_state'])
            # Update player stats from combat state
            game_state['player_stats'] = game_state['combat_state']['player']
        # Removed 'end_combat' logic from here
        else:
            game_state['message'] = "Invalid action during combat."
            game_state['options'] = combat.get_combat_options(game_state['combat_state'])

    # Handle ending combat *after* checking for active combat
    elif action == 'end_combat' and game_state.get('combat_state') is not None:
         # Player continues after winning/losing
         combat_state_ended = game_state['combat_state'] # Keep a reference before clearing
         victory = combat_state_ended.get('victory')
         # Restore player stats from combat outcome
         game_state['player_stats'] = combat_state_ended['player']
         game_state['combat_state'] = None # End combat

         if victory:
             # --- XP Gain and Level Up ---
             enemy_name = combat_state_ended.get('enemy', {}).get('name', None)
             base_xp_reward = 0
             enemy_level = 1 # Default enemy level if not found
             if enemy_name and enemy_name in combat.ENEMY_STATS:
                 enemy_stats = combat.ENEMY_STATS[enemy_name]
                 base_xp_reward = enemy_stats.get('xp_reward', 0)
                 enemy_level = enemy_stats.get('level', 1)

             final_xp_reward = base_xp_reward
             level_up_message = ""
             player_stats = game_state.get('player_stats')

             if base_xp_reward > 0 and player_stats:
                 player_level = player_stats.get('level', 1)
                 level_diff = player_level - enemy_level

                 # Apply XP reduction if player level is higher
                 if level_diff > 0:
                     reduction_percentage = level_diff * 0.20 # 20% reduction per level difference
                     # Clamp reduction between 0% and 90% (minimum 10% XP)
                     reduction_percentage = max(0, min(0.9, reduction_percentage))
                     final_xp_reward = math.ceil(base_xp_reward * (1 - reduction_percentage))

                 # Award the calculated XP
                 player_stats['xp'] += final_xp_reward
                 level_up_message = f"\nYou gained {final_xp_reward} XP!"
                 if final_xp_reward < base_xp_reward:
                     level_up_message += f" (Reduced from {base_xp_reward} due to level difference)"

                 # Check for level up (can happen multiple times)
                 while game_state['player_stats']['xp'] >= game_state['player_stats']['xp_to_next_level']:
                     current_level = game_state['player_stats']['level']
                     xp_needed = game_state['player_stats']['xp_to_next_level']

                     game_state['player_stats']['level'] += 1
                     game_state['player_stats']['xp'] -= xp_needed
                     game_state['player_stats']['stat_points'] += 5 # Award stat points
                     # Calculate XP needed for the *new* next level
                     game_state['player_stats']['xp_to_next_level'] = calculate_xp_for_next_level(game_state['player_stats']['level'])

                     level_up_message += f"\n**LEVEL UP!** You reached level {game_state['player_stats']['level']}!"
                     level_up_message += f"\nYou have {game_state['player_stats']['stat_points']} stat points to spend."

             # --- Proceed with location change ---
             next_location_id = game_state.pop('location_before_combat', None) # Get and remove intended destination
             if next_location_id:
                 game_state['previous_location'] = current_location # Where combat happened
                 game_state['current_location'] = next_location_id
                 location_data = locations.get_location_data(next_location_id, game_state)
                 # Use the enemy name from the *ended* combat state (already fetched above)
                 enemy_display_name = enemy_name if enemy_name else 'the enemy'
                 game_state['message'] = f"Having defeated the {enemy_display_name}, you arrive at the {next_location_id.replace('_', ' ')}."
                 game_state['message'] += level_up_message # Add XP/Level up info
                 game_state['message'] += "\n\n" + location_data.get('message', '') # Add location description
                 game_state['options'] = location_data.get('options', [])
             else:
                 # Fallback if location_before_combat wasn't set (shouldn't happen)
                 game_state['message'] = "You are victorious!"
                 game_state['message'] += level_up_message # Add XP/Level up info
                 # Stay in current location (where combat happened) - refresh options
                 location_data = locations.get_location_data(current_location, game_state)
                 game_state['options'] = location_data.get('options', [])

         else:
             # Player lost - Game Over or return to camp?
             game_state['message'] = "You have been defeated. You awaken back at your camp, weakened."
             # Reset location to main camp
             game_state['current_location'] = 'main_camp'
             # Optionally penalize player (e.g., reduce max health slightly?)
             # game_state['player_stats']['max_health'] = max(10, game_state['player_stats']['max_health'] - 10)
             game_state['player_stats']['health'] = game_state['player_stats']['max_health'] # Restore health
             location_data = locations.get_location_data('main_camp', game_state)
             game_state['message'] += "\n\n" + location_data['message']
             game_state['options'] = location_data['options']

    elif current_location == 'character_creation':
        if action == 'submit_name':
            player_name = player_input if player_input else "Hero"
            # Initialize player stats (using defaults from original Combat.py)
            # Initialize player stats including level-up system attributes
            initial_level = 1
            initial_xp_needed = calculate_xp_for_next_level(initial_level)
            game_state['player_stats'] = {
                'name': player_name, 'health': 100, 'max_health': 100,
                'attack': 10, 'defense': 5, 'is_player': True, 'is_defending': False,
                'level': initial_level,
                'xp': 0,
                'xp_to_next_level': initial_xp_needed,
                'stat_points': 0, # Start with 0 points
                'inventory': [], # Initialize empty inventory
                'equipment': {'weapon': 'fists'} # Start with fists equipped
            }
            game_state['current_location'] = 'main_camp'
            game_state['previous_location'] = 'character_creation'
            location_data = locations.get_location_data('main_camp', game_state)
            game_state['message'] = f"Welcome, {player_name}! Your adventure begins.\n\n{location_data['message']}"
            game_state['options'] = location_data['options']
        else:
             game_state['message'] = "Please enter your name."
             # Keep options the same

    elif action == 'go':
        next_location_id = None
        # Determine next location based on current location and direction
        if current_location == 'main_camp':
            if direction == 'north': next_location_id = 'fork'
            elif direction == 'east': next_location_id = 'forest'
            elif direction == 'south': next_location_id = 'ocean'
            elif direction == 'west': next_location_id = 'mountains'
        elif current_location == 'fork':
            if direction == 'left': next_location_id = 'left_path'
            elif direction == 'right': next_location_id = 'right_path'
            elif direction == 'back': next_location_id = 'main_camp' # Explicit back
        elif current_location == 'left_path':
            if direction == 'cave': next_location_id = 'damp_cave'
            elif direction == 'back': next_location_id = 'fork' # Explicit back
        elif current_location == 'right_path':
            if direction == 'back': next_location_id = 'fork' # Explicit back
            # Add other directions from right_path later if needed
        elif current_location == 'forest':
            if direction == 'back': next_location_id = 'main_camp' # Explicit back
            # 'explore_forest' is handled separately
        elif current_location == 'ocean':
            if direction == 'back': next_location_id = 'main_camp' # Explicit back
        elif current_location == 'mountains':
            if direction == 'back': next_location_id = 'main_camp' # Explicit back
        elif current_location == 'damp_cave':
            if direction == 'back': next_location_id = 'left_path' # Explicit back


        if next_location_id:
             # --- Check for Combat Encounters ---
             trigger_combat = False
             enemy_to_spawn = None
             # Define areas where combat can occur and their enemies
             combat_zones = {
                 'forest': 'Goblin',
                 'ocean': 'Giant Crab',
                 'mountains': 'Mountain Goat', # Or maybe random between Goat/Bat?
                 'left_path': 'Cave Bat',
                 'right_path': 'Cave Bat',
                 'damp_cave': 'Slime' # Added Slime encounter for Damp Cave
             }

             # Check if moving into a combat zone (and not already there)
             if next_location_id in combat_zones and current_location != next_location_id:
                 encounter_chance = random.randint(1, 100)
                 if encounter_chance <= 50: # 50% chance
                     trigger_combat = True
                     enemy_to_spawn = combat_zones[next_location_id]
                     # Could add randomness here too:
                     # if next_location_id == 'mountains':
                     #     enemy_to_spawn = random.choice(['Mountain Goat', 'Cave Bat'])

             if trigger_combat and enemy_to_spawn:
                 # Start combat
                 game_state['combat_state'] = combat.start_combat(game_state['player_stats'], enemy_to_spawn)
                 game_state['message'] = game_state['combat_state']['turn_message']
                 game_state['options'] = combat.get_combat_options(game_state['combat_state'])
                 # Keep track of where player was heading before combat started
                 game_state['location_before_combat'] = next_location_id
                 # Keep track of where player was heading before combat started
                 game_state['location_before_combat'] = next_location_id
                 # Don't update current_location or previous_location yet, stay in combat mode
             else:
                 # No combat or not entering a combat zone, proceed with normal location change
                 # Clear location_before_combat if it exists from a previous interrupted combat
                 game_state.pop('location_before_combat', None)
                 game_state['previous_location'] = current_location
                 game_state['current_location'] = next_location_id
                 location_data = locations.get_location_data(next_location_id, game_state)
                 # Add a message if player avoided combat
                 no_combat_message = ""
                 if next_location_id in combat_zones and current_location != next_location_id:
                      no_combat_message = f"You enter the {next_location_id.replace('_', ' ')}, but find it quiet for now.\n\n"

                 game_state['message'] = no_combat_message + location_data.get('message', "You arrive.")
                 game_state['options'] = location_data.get('options', [])
                 # Handle potential errors from get_location_data
                 if location_data.get('next_location'):
                     game_state['current_location'] = location_data['next_location']

        else:
            # This case handles invalid directions for the current location
            game_state['message'] = "You can't go that way from here."
            # Keep options the same

    elif action == 'rest':
        if current_location == 'main_camp':
            # Heal player fully
            if game_state['player_stats']:
                game_state['player_stats']['health'] = game_state['player_stats']['max_health']
                game_state['message'] = "You rest at the camp and feel fully recovered."
            else:
                 game_state['message'] = "You rest for a while."
            # Keep options the same (main camp options)
            location_data = locations.get_location_data('main_camp', game_state)
            game_state['options'] = location_data['options']
        else:
            game_state['message'] = "You can only rest at the main camp."
            # Keep options the same

    elif action == 'explore_forest':
         if current_location == 'forest':
             # Add more detailed exploration logic later
             # For now, maybe trigger another encounter chance?
             game_state['message'] = "You explore deeper into the woods... (More content needed here)"
             # Keep forest options for now
             location_data = locations.get_location_data('forest', game_state)
             game_state['options'] = location_data['options']
         else:
              game_state['message'] = "You can only explore the forest when you are there."

    # --- Item Actions ---
    elif action == 'take_item' and game_state.get('player_stats'):
        item_id = data.get('item_id') # Get item_id from the action data
        if item_id:
            # Check if item exists (basic check for now)
            item_details = items.get_item_details(item_id)
            if item_details:
                # Add item to inventory if not already present
                if item_id not in game_state['player_stats'].get('inventory', []):
                    game_state['player_stats'].setdefault('inventory', []).append(item_id)
                    game_state['message'] = f"You picked up the {item_details['name']}."
                else:
                    game_state['message'] = f"You already have a {item_details['name']}." # Or handle stacking later
            else:
                game_state['message'] = "You try to take something, but it's not there."
        else:
             game_state['message'] = "Take what?" # Should not happen with button UI

        # Refresh location options after taking item (to remove the 'take' option)
        location_data = locations.get_location_data(current_location, game_state)
        game_state['options'] = location_data.get('options', [])

    elif action == 'equip_weapon' and game_state.get('player_stats'):
        weapon_id = data.get('item_id') # Get weapon_id from the action data
        player_stats = game_state['player_stats']
        inventory = player_stats.get('inventory', [])
        equipment = player_stats.setdefault('equipment', {'weapon': 'fists'}) # Ensure equipment exists

        if weapon_id and weapon_id in inventory:
            # Unequip current weapon (if it's not fists) and put it back in inventory
            current_weapon = equipment.get('weapon')
            if current_weapon and current_weapon != 'fists':
                inventory.append(current_weapon)

            # Equip the new weapon
            equipment['weapon'] = weapon_id
            inventory.remove(weapon_id) # Remove from inventory
            weapon_details = items.get_item_details(weapon_id)
            game_state['message'] = f"You equipped the {weapon_details.get('name', weapon_id)}."
        else:
            game_state['message'] = "You can't equip that."

        # Refresh location options (though likely unchanged by equipping)
        location_data = locations.get_location_data(current_location, game_state)
        game_state['options'] = location_data.get('options', [])

    elif action == 'unequip_weapon' and game_state.get('player_stats'):
        player_stats = game_state['player_stats']
        inventory = player_stats.setdefault('inventory', [])
        equipment = player_stats.setdefault('equipment', {'weapon': 'fists'})
        current_weapon = equipment.get('weapon')

        if current_weapon and current_weapon != 'fists':
            equipment['weapon'] = 'fists' # Equip fists
            inventory.append(current_weapon) # Add weapon back to inventory
            weapon_details = items.get_item_details(current_weapon)
            game_state['message'] = f"You unequipped the {weapon_details.get('name', current_weapon)} and equipped your Fists."
        else:
            game_state['message'] = "You don't have a weapon equipped (besides your fists)."

        # Refresh location options
        location_data = locations.get_location_data(current_location, game_state)
        game_state['options'] = location_data.get('options', [])


    # --- Stat Allocation Actions ---
    elif action.startswith('allocate_') and game_state.get('player_stats'):
        stat_to_increase = action.split('_')[1] # e.g., 'health', 'attack', 'defense'
        player_stats = game_state['player_stats']

        if player_stats.get('stat_points', 0) > 0:
            player_stats['stat_points'] -= 1
            point_spent = False
            if stat_to_increase == 'health':
                # Increase max health and heal by the same amount (common practice)
                increase_amount = 5 # Or adjust as desired
                player_stats['max_health'] += increase_amount
                player_stats['health'] += increase_amount
                game_state['message'] = f"Increased Max Health by {increase_amount}. You have {player_stats['stat_points']} points left."
                point_spent = True
            elif stat_to_increase == 'attack':
                player_stats['attack'] += 1
                game_state['message'] = f"Increased Attack by 1. You have {player_stats['stat_points']} points left."
                point_spent = True
            elif stat_to_increase == 'defense':
                player_stats['defense'] += 1
                game_state['message'] = f"Increased Defense by 1. You have {player_stats['stat_points']} points left."
                point_spent = True

            if not point_spent:
                 # Invalid stat type, refund point (shouldn't happen with button UI)
                 player_stats['stat_points'] += 1
                 game_state['message'] = f"Invalid stat to allocate: {stat_to_increase}"
        else:
            game_state['message'] = "You have no stat points to spend."

        # Refresh options based on current location after allocation
        location_data = locations.get_location_data(current_location, game_state)
        game_state['options'] = location_data.get('options', [])

    else:
        # Handle unknown actions or actions not applicable to the current state
        game_state['message'] = f"Invalid action '{action}' here."
        # Attempt to refresh options for the current state
        if combat_active:
             game_state['options'] = combat.get_combat_options(game_state['combat_state'])
        elif current_location:
             location_data = locations.get_location_data(current_location, game_state)
             game_state['options'] = location_data.get('options', [])
        # else: options remain as they were (e.g., character creation)


    # --- End Game Logic Integration ---

    session['game_state'] = game_state
    # Return the updated state to the frontend, ensuring player stats reflect combat if active
    response_state = game_state.copy()
    if response_state.get('combat_state') and not response_state['combat_state'].get('is_over'):
        response_state['player_stats'] = response_state['combat_state']['player']

    return jsonify(response_state)

if __name__ == '__main__':
    # Use environment variable for port if available (e.g., for deployment)
    port = int(os.environ.get('PORT', 5000))
    # Run in debug mode for development (auto-reloads)
    # Set debug=False for production
    app.run(debug=True, host='0.0.0.0', port=port)
