# ChessGate

ChessGate compiles digital logic circuits into chess positions on an infinite chess board. It takes Verilog hardware descriptions, synthesizes them down to NAND gates, and encodes the resulting circuit as arrangements of chess pieces.

## How It Works

```
Verilog → Yosys (NAND synthesis) → Netlist JSON → Chess piece layout → Infinite chess format
```

Each NAND gate is represented as a specific pattern of chess pieces (pawns, bishops, knights, etc.) on the board. Gates are arranged in columns by circuit depth, with wires connecting layers.

## Prerequisites

- [Yosys](https://github.com/YosysHQ/yosys) 0.54+ (open-source synthesis suite)
- Python 3.6+
- No Python package dependencies (stdlib only)

## Quick Start

### 1. Synthesize a Verilog module to NAND gates

```bash
cd synthesis
yosys synth.ys
```

This reads `add1.v` (a 2-bit adder), synthesizes it to NAND-only logic, and writes:
- `output/fn_nand.json` — netlist in JSON format
- `output/fn_nand.v` — synthesized Verilog
- `output/fn_nand.png` — circuit diagram

To synthesize a different module, edit `synth.ys` and change `read_verilog add1.v` to your file.

### 2. Convert the netlist to chess positions

```bash
cd chesspiler
python3 gate_to_chess.py ../synthesis/output/fn_nand.json fn
```

Arguments:
- First arg: path to the Yosys JSON netlist
- Second arg: module name (default: `fn`)

Output is saved to `output/fn_nand_chess.txt` in infinite chess format (`v0;piece_id,x,y;...`).

### 3. (Optional) Inspect the board as a 2D array

```bash
python3 txt_to_board.py output/fn_nand_chess.txt --min-x 0 --max-x 50 --min-y 0 --max-y 20
```

### 4. (Optional) Analyze the gate netlist

```bash
python3 parse_gates.py ../synthesis/output/fn_nand.json fn
```

Prints gate connectivity, depth layers, and circuit summary statistics.

## Project Structure

```
synthesis/
  add1.v              # Example: 2-bit increment circuit
  sha256.v            # Example: SHA-256 round function
  synth.ys            # Yosys synthesis script
  output/             # Synthesis outputs

chesspiler/
  parse_gates.py      # Parse Yosys JSON netlist into layered gate graph
  gate_to_chess.py    # Convert gate graph to chess piece positions
  txt_to_board.py     # Convert infinite chess format to 2D board array
  output/             # Generated chess position files
```
