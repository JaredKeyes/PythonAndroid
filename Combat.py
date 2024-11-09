import random

class Character:
    def __init__(self, name, health, attack, defense):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense

    def take_damage(self, damage):
        self.health -= max(0, damage - self.defense)

    def is_alive(self):
        return self.health > 0

    def attack_target(self, target):
        damage = random.randint(self.attack - 2, self.attack + 2)
        target.take_damage(damage)
        print(f"{self.name} attacks {target.name} for {damage} damage!")

def combat(player, enemy):
    while player.is_alive() and enemy.is_alive():
        print(f"\n{player.name}'s health: {player.health}")
        print(f"{enemy.name}'s health: {enemy.health}")

        action = input("Attack or defend? (a/d): ").lower()

        if action == "a":
            player.attack_target(enemy)
        elif action == "d":
            player.defense += 2
            print(f"{player.name} defends, increasing defense!")
        else:
            print("Invalid action!")

        if enemy.is_alive():
            enemy.attack_target(player)

    if player.is_alive():
        print(f"You defeated {enemy.name}!")
    else:
        print(f"You were defeated by {enemy.name}!")

# Create player and enemy characters
player = Character("Hero", 100, 10, 5)
enemy = Character("Goblin", 50, 8, 2)

# Start combat
combat(player, enemy)