def fork():
	print("\nAfter following the road for a while, you come to a fork in the road.\n")
	choice = input("Do you want to go LEFT or RIGHT or head BACK to camp?\n").lower()

	if choice == "left":
		import Left
		Left.left()
	elif choice == "right":
		import Right
		Right.right()
	elif choice == "back":
		import MainCamp as mc
		mc.main_camp()
	else:
		print("That is not a valid choice.")