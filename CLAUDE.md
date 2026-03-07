# ChessGate

Converts digital logic circuits into chess positions on an infinite chess board.

## Pipeline

1. **Verilog** (`synthesis/`) → Yosys synthesizes to NAND-only gates
2. **Netlist parsing** (`chesspiler/parse_gates.py`) → extracts gate graph with depth layers
3. **Chess compilation** (`chesspiler/gate_to_chess.py`) → places gates as chess piece patterns on a board
4. **Output** → infinite chess format string (`v0;piece_id,x,y;...`)

## Project Structure

```
synthesis/           # Verilog sources and Yosys synthesis
  add1.v             # 2-bit adder (working test circuit)
  sha256.v           # SHA-256 round function (not yet synthesized)
  synth.ys           # Yosys synthesis script
  output/            # Synthesis outputs (JSON netlist, Verilog, PNG diagram)

chesspiler/          # Python pipeline (no external dependencies)
  parse_gates.py     # Parse Yosys JSON netlist → layered gate graph
  gate_to_chess.py   # Gate graph → chess board positions
  txt_to_board.py    # Infinite chess format → Python 2D array
  output/            # Generated chess position files
```

## Key Conventions

- Gate IDs: `g<N>` for NAND gates, `i<N>` for inputs, `o<N>` for outputs, `w<N>` for wires
- Board format: internally `self.pieces = {(x,y): piece}` dict, converted to 2D array at save time
- Infinite chess format: `v0;piece_id,x,y;...` where piece_id is 0-11
- Each NAND gate is an 18x15 chess piece pattern (`nand_position` in gate_to_chess.py)
- Layout is iterative: gate column → wire region → gate column → wire region → ...

## Board Structure & Wiring System

The board is a grid of **pawn columns** (even x) and **bishop columns** (odd x). Pawns and bishops form solid walls. Signals propagate via **knights** moving through specific gaps (removed bishops) in the walls.

### NAND Gate Connection Points (relative to gate bottom-left)
- **Input A**: left edge at `(1, 6)` — gap in bishop column
- **Input B**: left edge at `(1, 12)` — gap in bishop column
- **Output**: right edge at `(17, 5)` — gap in bishop column

### Horizontal Wires
Each wire is **2 rows tall** — two zigzag gap rows where the knight hops left-to-right:
- Lower row (`y_base`): gaps at odd x where `(x - x_start) % 4 == 1`
- Upper row (`y_base + 1`): gaps at odd x where `(x - x_start) % 4 == 3`

Knight path: `(1,lower) → (3,upper) → (5,lower) → (7,upper) → ...`

Wires share border rows with neighbors — the solid pawn/bishop rows between them are the default wall state.

### Vertical Movement (Parity Switching)
Horizontal wires use **mod0 parity** (gaps on one set of odd-x positions). To move vertically:
1. Switch to **mod1 parity** using a parity-switch construct (templates: `PARITY_SWITCH_DOWN`, `PARITY_SWITCH_UP` in gate_to_chess.py)
2. Move up/down on mod1 — knights on mod1 can freely cross mod0 horizontal wires since they're on different square parities and can never interact
3. Switch back to mod0 using the reverse construct

### Wire Routing Strategy
- **Default**: each wire goes straight horizontally at its source y-level
- **Vertical transition**: when source_y ≠ target_y, use parity switch → vertical → parity switch back
- **Crossings**: when two wires' source/target orderings swap, one must be rerouted (currently placeholder — underpass routing below gates)
- **Fan-out**: when one output feeds multiple inputs, gap patterns are unioned (overlaid)

### Current Status
- Gate placement, connection gathering, wall fill, and horizontal wire carving: **implemented**
- Parity switch templates: **defined but not yet stamped onto board**
- Vertical wire segments: **placeholder stub**
- Crossing resolution: **warning + naive routing**

## Building and Running

```bash
# Synthesize Verilog to NAND gates
cd synthesis && yosys synth.ys

# Convert netlist to chess positions
cd chesspiler && python3 gate_to_chess.py ../synthesis/output/fn_nand.json fn
```

## Dependencies

- Yosys (0.54+) for synthesis
- Python 3.6+ (stdlib only, no pip packages)
