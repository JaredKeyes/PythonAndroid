import random

def forest():
	encounter = random.randint(1, 100)
	print(encounter)
	if encounter < 100:
		import Combat
		player = Combat.Character("Hero", 100, 10, 5)
		enemy = Combat.Character("Goblin", 50, 8, 2)
		Combat.combat(player, enemy)
	print("\nYou arrive at the forest.\nYou can EXPLORE the forest.\nOr you can head BACK to camp.\n")
	choice = input("Which do you choose?\n").lower()
	
	if choice == "explore":
		print("You explore the forest.")
	elif choice == "back":
		import MainCamp as mc
		mc.main_camp()
	else:
		print("Not a valid choice.")