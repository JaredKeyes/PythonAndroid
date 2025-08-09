# Defines items in the game

# Using item IDs as keys for easy lookup
WEAPONS = {
    'fists': {
        'name': 'Fists',
        'attack_bonus': 0,
        'description': 'Your bare hands.'
    },
    'rusty_sword': {
        'name': 'Rusty Sword',
        'attack_bonus': 100, # Changed from 2 to 100
        'description': 'An old, surprisingly powerful sword.' # Updated description slightly
    },
    # Add more weapons later, e.g.:
    # 'dagger': {
    #     'name': 'Dagger',
    #     'attack_bonus': 1,
    #     'description': 'A small, sharp blade.'
    # }
}

# Could add ARMOR, CONSUMABLES etc. dictionaries here later

def get_item_details(item_id):
    """Returns the details for a given item ID, checking all item types."""
    if item_id in WEAPONS:
        return WEAPONS[item_id]
    # Add checks for other item types (ARMOR etc.) here if they exist
    return None # Item not found

def get_weapon_bonus(weapon_id):
    """Safely gets the attack bonus for a weapon ID."""
    weapon = WEAPONS.get(weapon_id)
    if weapon:
        return weapon.get('attack_bonus', 0)
    return 0 # Default to 0 if weapon not found or has no bonus
