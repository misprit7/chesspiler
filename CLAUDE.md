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
- Board format: `board_state[y][x]`, pieces are single chars (P/p, R/r, N/n, B/b, Q/q, K/k)
- Infinite chess format: `v0;piece_id,x,y;...` where piece_id is 0-11
- Each NAND gate is a 18x15 chess piece pattern (`nand_position` in gate_to_chess.py)
- Gates are laid out column-by-column (x += 35 per depth layer)

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
