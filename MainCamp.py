def main_camp():
	print("\nYou are at your main camp.\n")
	print("To the NORTH, there is a dirt road.\nTo the EAST is a dense forest.\nLooking SOUTH, you see a vast ocean.\nOff to the WEST is a large mountain range.\nYou can also stay at the camp and REST.\n") 
	choice = input("Which do you choose?\n").lower()
	
	if choice == "north":
		import Fork
		Fork.fork()
	elif choice == "east":
		import Forest
		Forest.forest()
	elif choice == "south":
		print("You go to the ocean.")
	elif choice == "west":
		print("You travel to the mountains.")
	elif choice == "rest":
		print("You rest for the day.")
	else:
		print("That's not a valid choice.")
	
main_camp()