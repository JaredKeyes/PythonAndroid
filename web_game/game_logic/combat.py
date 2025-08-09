import random

import math
from . import items # Import the new items module

class Character:
    """Represents a character in the game (player or enemy)."""
    def __init__(self, name, health, attack, defense, is_player=False, level=1, xp=0, xp_to_next_level=100, stat_points=0, inventory=None, equipment=None):
        self.name = name
        self.max_health = health # Store max health for potential healing later
        self.health = health
        self.attack = attack
        self.defense = defense
        self.is_player = is_player
        self.is_defending = False # Track if defending this turn
        # Player specific stats
        if self.is_player:
            self.level = level
            self.xp = xp
            self.xp_to_next_level = xp_to_next_level
            self.stat_points = stat_points
            # Initialize inventory and equipment only for player
            self.inventory = inventory if inventory is not None else []
            self.equipment = equipment if equipment is not None else {'weapon': 'fists'} # Default to fists

    def take_damage(self, damage):
        """Applies damage to the character, considering defense."""
        actual_damage = max(0, damage - self.defense)
        self.health -= actual_damage
        return actual_damage # Return damage taken for messaging

    def is_alive(self):
        """Checks if the character's health is above 0."""
        return self.health > 0

    def attack_target(self, target):
        """Calculates and applies attack damage to a target."""
        # Reset defense boost if player was defending
        if self.is_player and self.is_defending:
            self.defense -= 2 # Assuming a +2 boost for defense action
            self.is_defending = False

        # Calculate effective attack including weapon bonus for player
        effective_attack = self.attack
        if self.is_player and 'weapon' in self.equipment:
            effective_attack += items.get_weapon_bonus(self.equipment['weapon'])

        damage = random.randint(effective_attack - 2, effective_attack + 2)
        damage_taken = target.take_damage(damage)
        message = f"{self.name} attacks {target.name} for {damage} damage!"
        if damage_taken < damage:
            message += f" ({target.name} defended {damage - damage_taken} damage)"
        return message

    def defend(self):
        """Increases defense for the turn."""
        if not self.is_defending: # Prevent stacking defense boost
            self.defense += 2
            self.is_defending = True
        return f"{self.name} defends, increasing defense!"

    def get_state(self):
        """Returns a dictionary representation of the character's state."""
        # Start with basic stats common to all characters
        state = {
            'name': self.name,
            'health': self.health,
            'max_health': self.max_health,
            'attack': self.attack,
            'defense': self.defense,
            'is_player': self.is_player,
            'is_defending': self.is_defending,
        }
        # Add player specific stats if it's the player *before* returning
        if self.is_player:
            state.update({
                'level': self.level,
                'xp': self.xp,
                'xp_to_next_level': self.xp_to_next_level,
                'stat_points': self.stat_points,
                'inventory': self.inventory, # Add inventory
                'equipment': self.equipment  # Add equipment
            })
        return state # Return the potentially updated state dictionary

    @classmethod
    def from_state(cls, state):
        """Creates a Character instance from a state dictionary."""
        is_player = state.get('is_player', False)
        # Provide default values for new stats if they don't exist in the state (for backward compatibility)
        char = cls(
            state['name'],
            state['max_health'],
            state['attack'],
            state['defense'],
            is_player,
            level=state.get('level', 1) if is_player else 1,
            xp=state.get('xp', 0) if is_player else 0,
            xp_to_next_level=state.get('xp_to_next_level', 100) if is_player else 100,
            stat_points=state.get('stat_points', 0) if is_player else 0,
            # Load inventory/equipment, providing defaults if missing
            inventory=state.get('inventory', []) if is_player else None,
            equipment=state.get('equipment', {'weapon': 'fists'}) if is_player else None
        )
        char.health = state['health']
        char.is_defending = state.get('is_defending', False)
        return char

# --- Enemy Definitions ---
# Store enemy stats in a dictionary for easier management, including XP reward and level
ENEMY_STATS = {
    "Goblin":        {"health": 50, "attack": 8,  "defense": 2, "xp_reward": 10, "level": 1},
    "Giant Crab":    {"health": 60, "attack": 10, "defense": 6, "xp_reward": 15, "level": 3},
    "Cave Bat":      {"health": 35, "attack": 7,  "defense": 1, "xp_reward": 8,  "level": 2},
    "Mountain Goat": {"health": 70, "attack": 9,  "defense": 4, "xp_reward": 20, "level": 4},
    "Slime":         {"health": 30, "attack": 5,  "defense": 1, "xp_reward": 5,  "level": 1}, # Default/Fallback
}

# --- Combat Management Functions ---

def start_combat(player_state, enemy_type='Slime'):
    """Initializes combat state with a specific enemy type."""
    player = Character.from_state(player_state) # Recreate player object from state

    # Get stats for the requested enemy type, defaulting to Slime if unknown
    stats = ENEMY_STATS.get(enemy_type, ENEMY_STATS['Slime'])
    enemy = Character(enemy_type, stats['health'], stats['attack'], stats['defense'])

    combat_state = {
        'player': player.get_state(),
        'enemy': enemy.get_state(),
        'turn_message': f"A wild {enemy.name} appears!",
        'is_over': False,
        'victory': None # True for player win, False for player loss
    }
    return combat_state

def handle_combat_action(combat_state, action):
    """Processes a player action during combat."""
    player = Character.from_state(combat_state['player'])
    enemy = Character.from_state(combat_state['enemy'])
    messages = []

    if combat_state['is_over']:
        messages.append("Combat is already over.")
        return combat_state # No changes if combat finished

    # Player action
    if action == 'attack':
        messages.append(player.attack_target(enemy))
    elif action == 'defend':
        messages.append(player.defend())
    else:
        messages.append("Invalid action!")
        # Don't proceed to enemy turn if player action was invalid
        combat_state['player'] = player.get_state() # Update state even on invalid action
        combat_state['turn_message'] = "\n".join(messages)
        return combat_state

    # Check if enemy defeated
    if not enemy.is_alive():
        messages.append(f"You defeated {enemy.name}!")
        combat_state['is_over'] = True
        combat_state['victory'] = True
        combat_state['player'] = player.get_state() # Store final player state
        combat_state['enemy'] = enemy.get_state()   # Store final enemy state
        combat_state['turn_message'] = "\n".join(messages)
        return combat_state

    # Enemy action (simple AI: always attacks)
    messages.append(enemy.attack_target(player))

    # Check if player defeated
    if not player.is_alive():
        messages.append(f"You were defeated by {enemy.name}!")
        combat_state['is_over'] = True
        combat_state['victory'] = False
        # Player state is already updated by enemy attack
    else:
         # Reset player defense boost if they defended last turn but didn't attack this turn
         # (attack_target already handles this if they attacked)
        if player.is_defending and action != 'attack':
             player.defense -= 2
             player.is_defending = False


    # Update state
    combat_state['player'] = player.get_state()
    combat_state['enemy'] = enemy.get_state()
    combat_state['turn_message'] = "\n".join(messages)

    return combat_state

def get_combat_options(combat_state):
    """Returns available actions for the player in combat."""
    if combat_state['is_over']:
        # Options after combat ends (e.g., return to previous location)
        return [{'action': 'end_combat', 'text': 'Continue'}]
    else:
        return [
            {'action': 'combat_attack', 'text': 'Attack'},
            {'action': 'combat_defend', 'text': 'Defend'}
            # Add other combat actions like 'use_item', 'flee' later
        ]
