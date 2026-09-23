# fixture.pgn — hand-counted expectations

Eight Games. Four are eligible; four are dropped, each for a different reason.

| Game | Event                 | Elo (W/B)   | Result  | Plies | Notes                                   | Eligible? |
| ---- | --------------------- | ----------- | ------- | ----- | ---------------------------------------- | --------- |
| G1   | Rated Blitz game      | 1500 / 1500 | 1-0     | 20    | Ruy Lopez; 4 plies past Theory depth     | yes       |
| G2   | Rated Rapid game      | 2100 / 2050 | 1/2-1/2 | 16    | Same 16-ply Line as G1                   | yes       |
| G3   | Rated Bullet game     | 1000 / 1100 | 0-1     | 16    | 1.d4 d5 2.c4 e6 3.Nc3 Nf6 ... 4.Bg5       | yes       |
| G4   | Rated Blitz game      | 1300 / 1250 | 1-0     | 16    | 1.c4 e6 2.d4 d5 3.Nc3 Nf6 ... 4.Bg5 (transposes into G3's Position after move 3) | yes |
| G5   | Casual Blitz game     | 1500 / 1500 | 1-0     | 16    | Not rated                                | no |
| G6   | Rated Blitz game      | 1400 / 1450 | 1-0     | 10    | Shorter than the 16-Ply Theory depth     | no |
| G7   | Rated Blitz game      | 1600 / ?    | 1-0     | 16    | Black's Elo unknown                      | no |
| G8   | Rated Blitz game      | 1500 / 1500 | 1-0     | 16    | `Variant: Chess960`, not standard chess  | no |

## Expected rows at the starting Position

| Continuation (UCI) | Rating band | Speed | White wins | Draws | Black wins | From |
| ------------------- | ----------- | ----- | ---------- | ----- | ---------- | ---- |
| e2e4                | 1200_1599   | blitz | 1          | 0     | 0          | G1   |
| e2e4                | 2000_plus   | rapid | 0          | 1     | 0          | G2   |
| d2d4                | under_1200  | bullet| 0          | 0     | 1          | G3   |
| c2c4                | 1200_1599   | blitz | 1          | 0     | 0          | G4   |

Total Games represented at the starting Position: **4** (only G1-G4; G5-G8 contribute nothing anywhere in the table).

## Transposition: G3 and G4 merge after 3 full moves

G3's Line (1.d4 d5 2.c4 e6 3.Nc3 Nf6) and G4's Line (1.c4 e6 2.d4 d5 3.Nc3 Nf6) reach the identical board (same piece placement, side to move, castling rights, en passant) after 6 plies, and both continue 4.Bg5. So the table has **one** Position with **two** `c1g5` (Bg5) rows — one per Game's Rating band/Speed, since those stay part of the grouping key:

| Rating band | Speed  | White wins | Draws | Black wins | From |
| ----------- | ------ | ---------- | ----- | ---------- | ---- |
| under_1200  | bullet | 0          | 0     | 1          | G3   |
| 1200_1599   | blitz  | 1          | 0     | 0          | G4   |

## Theory depth: G1's 17th ply is dropped

G1 is 20 plies long. Only the first 16 (through 8...O-O) are ingested; `9. h3` (`h2h3`) must not appear as a Continuation from the Position reached after those 16 plies.
