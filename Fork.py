from Left import *
from Right import *

def fork():
	choice1 = input("You come across a fork in the road. Do you go left or right?\n").lower()

	if choice1 == "left":
		left()
	elif choice1 == "right":
		right()
	else:
		print("That is not a valid choice.")