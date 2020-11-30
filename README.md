# Borkle Games
This is a django based web app that hosts some games I have built for fun.
The games use Javascript to allow asnycronous play with one more players.

Figuring out how to sync multiple players to create a smooth game play experience
was an opportunity to beef up my Javascript and front end skills. The mental challenge
of how to organize games, game players, turns, and rules into a database model was
an exceptionally fun puzzle to solve.

# Usage
Feel free to clone and run the games locally, but it's a lot more fun with friends.
You can visit the live version of the project at https://borkle.app.

Have fun!

# Technical Details
## Bogames
This app is a base app for each individual game in the application, since the basic behavior and
components of each game is very similar. 

Each game has a Game class which inherets from bogames.models.game and should have its own
indepenedent GamePlayer class and Turn classes. 

The properties of GamePlayer and Turn classes are unique to a game.

THe bogames app also includes several base Views for setting up game dashboards and other common
interactions such as joining or declining games.

## Borkle

![screenshot of borkle dice game](https://github.com/astromitts/borkle-social/blob/main/screenshots/borkle-gameplay.png?raw=true)

This is a dice based game similar to the game Farkle. 

For each turn, each player starts with 6 dice to roll. They continue rolling as long as they continue
landing at least one scoring combination until they end their turn or roll a non-scoring set.

Once a player has reached the game's max score, all other players get one more turn.

The final player or players with the highest score win.

## BoatFight
This is a board game based on battleship. 

For each game, players place boats on their game board in the setup phase.

![screenshot of boat fight placement screen](https://github.com/astromitts/borkle-social/blob/main/screenshots/boatfight-setup.png?raw=true)

In the play phase, each player has either 1 shot (classic style) or up to 5 
shots (salvo style - 1 shot per boat you still have floating) to try to sink
their opponent's boats. 

![screenshot of boat fight play screen](https://github.com/astromitts/borkle-social/blob/main/screenshots/boatfight-playshot.png?raw=true)

The first player to sink all 5 of their opponent's boats wins. 
