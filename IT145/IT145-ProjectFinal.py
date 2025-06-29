"""
Author: Nathaniel Gratton
Date: Feb/12/2023 (Refreshed: May/20/2025)
Description: Vampire Mansion - A text-based adventure game to collect items and defeat a vampire.
"""

# Room setup: directions, items, and descriptions now unified
rooms = {
    'Foyer': {
        'East': 'Living Room',
        'Item': None,
        'Description': "You stand in the foyer of a looming mansion. The air is cold, the floor creaks, and faint whispers seem to dance through the air. A single door lies to the East."
    },
    'Living Room': {
        'West': 'Foyer',
        'North': 'Kitchen',
        'South': 'Basement',
        'East': 'Master Bedroom',
        'Item': 'Study Key',
        'Description': "Dusty curtains hang half-drawn over the tall windows. A tattered couch sits in the middle, and on a nearby coffee table lies a small metal key — oddly polished."
    },
    'Kitchen': {
        'South': 'Living Room',
        'East': 'Dining Room',
        'Item': 'Knife',
        'Description': "Pots hang from a rack above a counter. One in particular — a sharp kitchen knife — looks recently used. A sour scent lingers in the air."
    },
    'Dining Room': {
        'West': 'Kitchen',
        'Item': 'Armor',
        'Description': "A long oak table dominates the room. In the corner stands a tall statue clad in ancient armor, its gaze watching you."
    },
    'Master Bedroom': {
        'West': 'Living Room',
        'North': 'Study',
        'Item': 'Bracelet',
        'Description': "Torn drapes filter pale light into the room. A silver bracelet rests on the bedside table, missing what looks like a gemstone setting."
    },
    'Study': {
        'South': 'Master Bedroom',
        'Item': 'Basement Key',
        'Description': "Bookcases line the walls. A heavy desk sits in the center, and something shiny — another key? — glints from beneath a paperweight."
    },
    'Basement': {
        'North': 'Living Room',
        'East': 'Dungeon',
        'Item': 'Gemstone',
        'Description': "You descend into darkness. Boxes are stacked high, and atop one rests a velvet pouch. Something inside pulses faintly with light."
    },
    'Dungeon': {
        'West': 'Basement',
        'Item': 'Vampire',
        'Description': "You’ve entered the lair of the vampire. Candles flicker as he chants a ritual. The air is heavy — this is your final chance to act."
    }
}

inventory = []
current_room = 'Foyer'

def help_msg():
    print("\nCommands:")
    print(" go [direction]   - move between rooms")
    print(" take [item]      - pick up an item")
    print(" inventory        - view your inventory")
    print(" help             - display this help message")
    print(" exit             - quit the game")

def describe_room():
    print(f"\nYou are in the {current_room}.")
    print(rooms[current_room]['Description'])
    if rooms[current_room].get('Item') and rooms[current_room]['Item'] != 'Vampire':
        print(f"You see a {rooms[current_room]['Item']} here.")
    print("Exits: " + ", ".join([k for k in rooms[current_room] if k in ['North', 'South', 'East', 'West']]))

def move(direction):
    global current_room
    if direction in rooms[current_room]:
        next_room = rooms[current_room][direction]
        if next_room == 'Study' and 'Study Key' not in inventory:
            print("The study door is locked. You need a key.")
            return
        if next_room == 'Basement' and 'Basement Key' not in inventory:
            print("The basement door is locked. You need a key.")
            return
        current_room = next_room
        describe_room()
    else:
        print("There is no exit that way.")

def get_item(item):
    room_item = rooms[current_room].get('Item')
    if room_item and room_item.lower() == item.lower():
        inventory.append(room_item)
        rooms[current_room]['Item'] = None
        print(f"{room_item} has been added to your inventory.")
    else:
        print("That item couldn’t be found.")

def main():
    global current_room
    print('Welcome to "Vampire Mansion"')
    help_msg()
    describe_room()

    while True:
        command = input("\nWhat would you like to do? ").lower().split()

        if not command:
            continue

        if command[0] == 'go':
            if len(command) > 1:
                move(command[1].capitalize())
            else:
                print("Go where?")
        elif command[0] == 'take':
            if len(command) > 1:
                get_item(' '.join(command[1:]))
            else:
                print("Take what?")
        elif command[0] == 'inventory':
            print("Inventory:", ", ".join(inventory) if inventory else "Empty")
        elif command[0] == 'help':
            help_msg()
        elif command[0] == 'exit':
            print("Thanks for playing!")
            break
        else:
            print("That is not a valid command.")

        if current_room == 'Dungeon':
            required_items = ['Armor', 'Knife', 'Bracelet', 'Gemstone']
            if all(item in inventory for item in required_items):
                print("\nYou confront the vampire with all your items. The bracelet glows, and you defeat the evil creature!")
                print("Congratulations! You have saved your town.")
            else:
                print("\nYou face the vampire unprepared... and perish.")
            break

if __name__ == '__main__':
    main()
