import Fork

def main_camp():
	print("You are at your main camp.")
	choice = input("Would you like to go to the fork? Yes or No?\n").lower()
	
	if choice == "yes":
		Fork.fork()
	elif choice == "no":
		print("You rest for the day.")
	else:
		print("That's not a valid choice.")
	
main_camp()