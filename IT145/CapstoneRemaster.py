"""
Author: Nathaniel Gratton
Date: Feb/12/2023 (Refreshed: May/20/2025)
Description: Vampire Mansion - A text-based adventure game to collect items and defeat a vampire.
"""

import json
import os
import random
import time

# --------- Puzzle Initialization ---------
birthdays = [("January", 3), ("April", 17), ("October", 10), ("December", 25)]
month_name, day = random.choice(birthdays)
month_num = time.strptime(month_name, "%B").tm_mon
valid_codes = [f"{month_num:02}{day:02}", f"{day:02}{month_num:02}"]

true_statements = ["The dining room has an oak table.", "The living room has dusty curtains.", "The foyer creaks with age."]
false_statements = ["The kitchen has marble countertops.", "The basement smells of herbs.", "The study contains a fireplace."]
truth_box = random.choice(["Red", "Green", "White"])
truth_statement = random.choice(true_statements)
false_boxes = [b for b in ["Red", "Green", "White"] if b != truth_box]
box_statements = {
    truth_box: truth_statement,
    false_boxes[0]: false_statements[0],
    false_boxes[1]: false_statements[1]
}

rooms = {
    'Foyer': {
        'East': 'Living Room',
        'Item': None,
        'Description': "You stand in the foyer of a looming mansion. The air is cold, the floor creaks..."
    },
    'Living Room': {
        'West': 'Foyer', 'North': 'Kitchen', 'South': 'Basement', 'East': 'Master Bedroom',
        'Item': 'Study Key',
        'Description': "Dusty curtains hang over the tall windows..."
    },
    'Kitchen': {
        'South': 'Living Room', 'East': 'Dining Room',
        'Item': None,
        'Note': f"Grandma's birthday is {month_name} {day}.",
        'Description': "A sour scent lingers in the air. A note is stuck to the fridge."
    },
    'Dining Room': {
        'West': 'Kitchen',
        'Item': 'Armor',
        'Description': "A long oak table dominates the room. A statue blocks your way."
    },
    'Master Bedroom': {
        'West': 'Living Room', 'North': 'Study',
        'Item': 'Bracelet',
        'Description': "A silver bracelet rests on the table."
    },
    'Study': {
        'South': 'Master Bedroom',
        'Item': None,
        'Locked': True,
        'Description': "A heavy desk sits in the center. A safe is embedded in the wall."
    },
    'Basement': {
        'North': 'Living Room', 'East': 'Dungeon',
        'Item': None,
        'Description': "Boxes are stacked high. Three colored ones stand out: Red, Green, White."
    },
    'Dungeon': {
        'West': 'Basement',
        'Item': 'Vampire',
        'Description': "Candles flicker. The vampire stirs."
    }
}

inventory = []
current_room = 'Foyer'
puzzles = {
    'riddle_solved': False,
    'safe_unlocked': False,
    'gem_obtained': False,
    'bracelet_combined': False
}

def save_game():
    with open("savegame.json", "w") as f:
        json.dump({
            "current_room": current_room,
            "inventory": inventory,
            "puzzles": puzzles,
            "valid_codes": valid_codes,
            "truth_box": truth_box,
            "box_statements": box_statements
        }, f)
    print("Game saved.")

def load_game():
    global current_room, inventory, puzzles, valid_codes, truth_box, box_statements
    if os.path.exists("savegame.json"):
        with open("savegame.json", "r") as f:
            data = json.load(f)
            current_room = data["current_room"]
            inventory = data["inventory"]
            puzzles = data["puzzles"]
            valid_codes = data["valid_codes"]
            truth_box = data["truth_box"]
            box_statements = data["box_statements"]
        print("Game loaded.")
    else:
        print("No save found.")

def describe_room():
    room = rooms[current_room]
    print(f"\nYou are in the {current_room}.")
    print(room['Description'])
    if 'Note' in room:
        print("Note: " + room['Note'])
    if room.get('Item') and room['Item'] not in inventory:
        print(f"You see a {room['Item']} here.")
    print("Exits: " + ", ".join([k for k in room if k in ['North', 'South', 'East', 'West']]))

def help_msg():
    describe_room()
    print("\nCommands:")
    print(" go [direction] - move between rooms")
    print(" take [item] - pick up an item")
    print(" inventory - view your inventory")
    print(" save - save your game")
    print(" load - load a saved game")
    print(" use - use an item or interact with a puzzle")
    print(" open [box] - check a colored box in the basement")
    print(" combine - use two items together")
    print(" interact / approach [object] - try to interact with objects")
    print(" help - show this message again")
    print(" exit - quit the game")

def parse_command(cmd):
    tokens = cmd.lower().split()
    if not tokens:
        return None, None
    synonyms = {
        'grab': 'take', 'collect': 'take', 'pick': 'take',
        'walk': 'go', 'run': 'go', 'head': 'go',
        'bag': 'inventory', 'check': 'inventory',
        'interact': 'riddle', 'approach': 'riddle'
    }
    action = synonyms.get(tokens[0], tokens[0])
    target = ' '.join(tokens[1:]) if len(tokens) > 1 else None
    return action, target

# --------- Main Game Loop ---------
def main():
    global current_room
    print('Welcome to "Vampire Mansion"')
    load_game()
    describe_room()

    while True:
        cmd = input("\nWhat would you like to do? ")
        action, target = parse_command(cmd)

        if action == 'go':
            if target:
                if target.capitalize() in rooms[current_room]:
                    next_room = rooms[current_room][target.capitalize()]
                    if next_room == 'Study' and not puzzles['safe_unlocked']:
                        print("The study is locked. A safe blocks your path.")
                    elif next_room == 'Basement' and 'Basement Key' not in inventory:
                        print("The basement door is locked.")
                    elif next_room == 'Dungeon' and not puzzles['bracelet_combined']:
                        print("You feel a magical force blocks the way.")
                    else:
                        current_room = next_room
                        describe_room()
                else:
                    print("There is no exit that way.")
            else:
                print("Go where?")

        elif action == 'take':
            room = rooms[current_room]
            item = room.get('Item')
            if current_room == 'Dining Room' and not puzzles['riddle_solved']:
                answer = input("The statue asks: 'I speak without a mouth and hear without ears. I have no body... What am I?'\n> ")
                if answer.strip().lower() == 'echo':
                    puzzles['riddle_solved'] = True
                    print("The statue removes its armor and places it in front of you.")
                else:
                    print("The statue remains still.")
                    continue
            if item and item.lower() == target:
                inventory.append(item)
                room['Item'] = None
                print(f"You took the {item}.")
            else:
                print("There is nothing like that here.")

        elif action == 'open' and current_room == 'Basement':
            if puzzles['gem_obtained']:
                print("You've already found the gemstone.")
                continue
            if target.capitalize() in ['Red', 'Green', 'White']:
                print("The box reads:", box_statements[target.capitalize()])
                if target.capitalize() == truth_box:
                    inventory.append('Gemstone')
                    puzzles['gem_obtained'] = True
                    print("You found the gemstone!")
                else:
                    print("The box is empty.")
            else:
                print("Which box? Red, Green, or White?")

        elif action == 'combine':
            if 'Bracelet' in inventory and 'Gemstone' in inventory:
                puzzles['bracelet_combined'] = True
                print("The gemstone clicks into the bracelet. A magic hum fills the air.")
            else:
                print("You can't combine those.")

        elif action == 'use' and current_room == 'Study' and not puzzles['safe_unlocked']:
            code = input("Enter the 4-digit code: ")
            if code in valid_codes:
                inventory.append('Basement Key')
                puzzles['safe_unlocked'] = True
                print("The safe opens. You got the Basement Key!")
            else:
                print("Wrong code.")

        elif action == 'inventory':
            print("Inventory:", ", ".join(inventory) if inventory else "Empty")

        elif action == 'save':
            save_game()

        elif action == 'load':
            load_game()
            describe_room()

        elif action == 'help':
            help_msg()

        elif action == 'riddle' and current_room == 'Dining Room':
            if not puzzles['riddle_solved']:
                print("The statue's eyes glow. It speaks: 'I turn once, what is out will not get in. I turn again, what is in will not get out. What am I?'")
                answer = input("Your answer: ").strip().lower()
                if answer == 'key':
                    print("The statue nods and steps aside. You may take the armor.")
                    puzzles['riddle_solved'] = True
                else:
                    print("The statue remains silent. That is not the correct answer.")
            else:
                print("The statue has already moved. You may take the armor.")

        elif action == 'exit':
            print("Thanks for playing!")
            break

        if current_room == 'Dungeon':
            if all(item in inventory for item in ['Armor', 'Knife']):
                print("\nYou are ready. You strike with your blade, the armor deflecting his final blow.")
                print("The vampire crumbles. You've won!")
            else:
                print("\nYou are not prepared. The vampire overwhelms you.")
            break

if __name__ == '__main__':
    main()
