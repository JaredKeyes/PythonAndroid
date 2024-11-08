def forest():
	print("\nYou arrive at the forest.\nYou can EXPLORE the forest.\nOr you can head BACK to camp.\n")
	choice = input("Which do you choose?\n").lower()
	
	if choice == "explore":
		print("You explore the forest.")
	elif choice == "back":
		import MainCamp as mc
		mc.main_camp()
	else:
		print("Not a valid choice.")