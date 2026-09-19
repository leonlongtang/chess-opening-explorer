# A Position is the board, not the Line

A Position is identified by the board itself (piece placement, side to move, castling rights, en passant), so Transpositions merge into one Position and their statistics are pooled. We rejected identifying a Position by its move sequence: it gives a simple tree, but the same board reached by different move orders would show split, misleading statistics.

## Consequences

The data is a graph, not a tree, so an unnamed Position has no single "parent" to inherit an Opening name from. The Explorer therefore carries the Line the user navigated and names the Position from that Line.
