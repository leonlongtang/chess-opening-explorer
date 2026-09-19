# Chess Opening Explorer

A tool for exploring how chess openings perform in real games: pick a Position, see which Continuations people play and how those games end, sliced by Rating band and Speed.

## Language

### Games and moves

**Game**:
A finished, rated, standard-chess game with a decisive or drawn result, known ratings for both players, and at least as many Plies as the Theory depth. Only such games are counted.
_Avoid_: Match, record

**Ply**:
One move by one side. A full chess move ("move 5") is two Plies.
_Avoid_: Turn, half-move

**Line**:
A specific sequence of Plies from the starting Position.
_Avoid_: Variation, path

**Position**:
A board state, identified by piece placement, side to move, castling rights and en passant availability, regardless of the Line that reached it.
_Avoid_: Node, state

**Transposition**:
Two different Lines that reach the same Position. They count as one Position.

**Theory depth**:
The Ply limit past which the explorer stops tracking Positions (currently 16).
_Avoid_: Horizon, max depth

### What the explorer shows

**Continuation**:
A move played from a Position in at least one Game, shown with its Outcome split and how often it was played.
_Avoid_: Next move, child, branch

**Rare Continuation**:
A Continuation played in fewer Games than the display threshold under the current filters. It is hidden from the Explorer but still counts toward its Position's totals.
_Avoid_: Minor move, outlier

**Outcome split**:
For a set of Games, how many were won by White, drawn, and won by Black.
_Avoid_: Win rate (ambiguous about which side)

**Explorer**:
The view of one Position, optionally narrowed by Rating band and Speed, listing its Continuations.
_Avoid_: Tree, browser

### Slicing

**Game rating**:
The average of White's and Black's Elo in a Game.
_Avoid_: Elo (per player, not per Game)

**Rating band**:
One of four ranges of Game rating: under 1200, 1200–1599, 1600–1999, 2000 and over.
_Avoid_: Bracket, tier

**Speed**:
The time-control category of a Game: bullet, blitz, rapid or classical.
_Avoid_: Time control (the raw setting, not the category)

### Naming

**Opening**:
A named Position from the opening reference, identified by an ECO code and a name.
_Avoid_: Variation, defense
