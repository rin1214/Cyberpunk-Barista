CYBERPUNK BARISTA
=================

A fast-paced cyberpunk café game made with Python and Pygame.

You are a barista working through a futuristic café shift. Customers arrive with
specific drink requirements, and your job is to prepare the order accurately and
quickly. The better you serve, the more XP and credits you earn. As you progress,
you can unlock new locations, drinks and more challenging customers. This game is
tend to be played during tense hours as a relaxing time.

The game is designed around a simple idea: making a drink is easy to understand,
but becoming a really good barista takes practice.


WHAT YOU CAN DO
----------------
- Enter a player name and start a new café shift.
- Choose a barista before starting the game.
- Receive customer orders through an interactive order scene.
- Prepare drinks using drink selection and customisation controls.
- Match four order attributes:
    * Drink
    * Temperature
    * Caffeine
    * Sweetness
- Complete an ingredient/preparation mini-game before blending.
- Serve the finished drink and receive customer reactions.
- Earn XP and credits from successful orders.
- Build combos by serving perfect drinks.
- Earn extra XP for serving customers quickly.
- Lose credits when an order is not completed correctly.
- Unlock new café locations through the map system.
- Unlock additional drinks as the player progresses.
- Meet different customer types with different patience and payment behaviour.
- Open the recipe book to check available drinks and ingredients.
- View a persistent local leaderboard.
- Save player progress locally and continue from the saved profile.
- Change audio settings and use the pause/menu system.
- Play different mini-game styles depending on the drink being prepared.
- Complete the final shift and view final statistics.


PROGRESSION
-----------
The game currently has three levels/locations:

Level 1 - Back Alley Kiosk
Level 2 - Neon Lounge
Level 3 - Cyber Penthouse

Players start with 100 credits. Higher locations require credits to unlock.
Each level also introduces additional drinks and customer possibilities.

There are currently nine drinks in the game:

Level 1
- Neon Latte
- Milkyway
- Void Chai

Level 2
- Cyber Fuel
- Hologram Frappe
- Pixel Lemint

Level 3
- Caramel Byte
- Stardust Matcha
- Meteorite


CUSTOMER SYSTEM
---------------
Customers are not just visual decoration. They have their own archetypes,
patience values and payment multipliers. The game currently includes:

- Runner
- Executive
- Hacker
- Drone Pilot
- Corporate Spy
- Cyberpunk Cat

The order system checks four attributes, so a drink can be partially correct
rather than simply being right or wrong. Customers also react after receiving
the drink and stay briefly before leaving, making the service interaction feel
more complete.


MINI-GAMES
----------
Different drinks can trigger different preparation challenges. The current
challenge system includes several styles, including:

- Match-3 ingredient matching
- Gravity shield / deflect challenge
- WASD lane-running challenge
- Circuit soldering challenge
- Neon dash
- Aim rush
- Rhythm rush

The challenges are connected to drink preparation rather than being completely
separate games, so the player has to complete the preparation step before the
drink can be finished.


REWARDS
-------
Perfect orders give XP and credits. Consecutive perfect orders build a combo,
and fast service can give additional XP.

The reward system is based on order accuracy:

4/4 correct - perfect order with the main reward
3/4 correct - customer reaction, but no perfect-order reward
2/4 correct - customer reaction, but no perfect-order reward
1/4 correct - customer reaction, but no perfect-order reward
0/4 correct - customer reaction and penalty

The game also shows reward popups so the player can immediately see what was
gained or lost.


CONTROLS
--------
Most gameplay interaction is mouse-based.

Main gameplay:
- Mouse click       Select drinks, customise the order, blend and serve
- F                  Open/close the café menu
- M                  Open the map
- L                  Open the leaderboard
- R                  Reset the current player progress
- 1 / 2 / 3         Switch to an unlocked level
- ESC               Used by several menus/screens to return or exit

Order scene:
- Mouse click       Skip/continue the dialogue
- SPACE / ENTER     Skip/continue the dialogue

Mini-games:
- Controls depend on the challenge. Instructions are shown inside each
  mini-game before it starts.
- Some challenges use A/D or LEFT/RIGHT.
- Some use SPACE/W/UP or mouse clicks.
- Rhythm and aim challenges mainly use the mouse.


HOW TO RUN
----------
Requirements:
- Python 3.10 or newer
- Pygame

Install Pygame:

    pip install pygame

Run the game from the project folder:

    python main.py

On Windows, if the Python launcher is being used:

    py main.py

The game stores player progress locally. Save data is created/updated by the
game and does not require an external database or internet connection.


PROJECT STRUCTURE
-----------------
main.py                 Main game loop and overall game flow
customer.py             Customer types, orders, reactions and movement
drink.py                Drink recipes, prices and validation
station.py              Drink preparation and café workstation
mini_challenges.py      Preparation mini-games
order_scene.py          Customer order / dialogue scene
recipe_book.py          Recipe book interface
progression.py          XP and level progression
rewards.py              XP, credits, combo and reward calculations
ui_economy.py           Credits, XP, levels and local save data
map_manager.py          Café locations and level unlocking
map_screen.py            Map interface
leaderboard_manager.py  Local leaderboard data
leaderboard_screen.py   Leaderboard interface
barista_selection.py    Barista selection and unlocks
start_screen.py         Player name and start screen
loading_screen.py       Loading/transition screens
level_unlock_screen.py  Level unlock presentation
game_end_screen.py      End-of-shift screen and final statistics
accuracy.py             Four-part order accuracy calculation
game_state.py           Drink preparation state management
audio_settings.py       Music and sound settings


DESIGN IDEA
-----------
The visual direction of Cyberpunk Barista is based on a neon cyberpunk café.
The game uses bright cyan, pink and purple UI elements, futuristic locations,
character sprites and drink artwork to keep the theme consistent across the
main gameplay, map, leaderboard, order scene and ending screens.

The main gameplay loop is:

    Customer arrives
          ->
    Receive order
          ->
    Select drink
          ->
    Complete preparation challenge
          ->
    Customise temperature/caffeine/sweetness
          ->
    Blend and assemble
          ->
    Serve customer
          ->
    Accuracy + reward + reaction
          ->
    Customer leaves
          ->
    Next customer

The intention is to make the player gradually move from simply completing
orders to managing accuracy, speed, money, XP, combos and progression.


TROUBLESHOOTING
---------------
If the game does not start:

1. Make sure Python 3.10+ is installed.
2. Install Pygame with:
       pip install pygame
3. Make sure you run main.py from the project folder.
4. Make sure the assets folder remains beside the Python files.
5. Do not rename or move the assets subfolders unless the corresponding paths
   in the source code are also updated.

If a player's local progress needs to be reset, use the in-game R reset option
or remove the relevant local save data and start again.


FINAL NOTE
----------
Cyberpunk Barista was built as a Pygame software project with a focus on
interactive gameplay, progression, preparation challenges and a complete café
service loop. The project intentionally combines several smaller systems into
one playable experience rather than relying on a single simple mechanic.

Enjoy the shift. Keep the customers happy. Don't burn the coffee.
