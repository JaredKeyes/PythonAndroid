def character_creation():
    name = input("What is your name?\n")
    gender = input("Are you male or female?\n")
    height = input("Enter your height in centimeters\n")
    body_type = input("Choose your body type: Slim, Average, Strong, Overweight\n")
    eye_color = input("What color are your eyes?\n")
    hair_color = input("What color is your hair?\n")

    str = 10
    dex = 10
    con = 10
    sma = 10
    wis = 10
    cha = 10

    print(f"Hello {name}, you are a {height} centimeter {gender} with {eye_color} eyes and {hair_color} hair. You have a {body_type} build. These are your stats.")
    print(f"Strength: {str}")
    print(f"Dexterity: {dex}")
    print(f"Constitution: {con}")
    print(f"Intelligence: {sma}")
    print(f"Wisdom: {wis}")
    print(f"Charisma: {cha}")
    finalize = input("Ready for your adventure? YES or NO\n").lower()
    if finalize == "yes":
        import MainCamp as mc
        mc.main_camp()
    elif finalize == "no":
        character_creation()
    else:
        print("That is an invalid selection. Please try again.")

character_creation()

