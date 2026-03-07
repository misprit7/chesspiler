#!/usr/bin/env python3
"""
Convert synthesized NAND gates to chess positions.

This program takes the output from parse_gates.py and converts each gate
into a chess position representation as an infinite chess board where
each coordinate (x,y) is either occupied by a piece or empty.
"""

import json
from dataclasses import dataclass, field
from typing import Tuple, Optional, List
from parse_gates import analyze_netlist

# Map pieces to template IDs based on editor.js
piece_to_id = {
    'P': 0,  # White Pawn
    'p': 1,  # Black Pawn
    'R': 2,  # White Rook
    'r': 3,  # Black Rook
    'N': 4,  # White Knight
    'n': 5,  # Black Knight
    'B': 6,  # White Bishop
    'b': 7,  # Black Bishop
    'Q': 8,  # White Queen
    'q': 9,  # Black Queen
    'K': 10, # White King
    'k': 11, # Black King
}

nand_position = [
    ['P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B'],
    ['P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B'],
    ['P', '.', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B'],
    ['P', 'B', 'P', '.', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B'],
    ['P', 'B', 'P', 'B', 'P', '.', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B'],
    ['P', 'B', 'P', '.', 'P', 'P', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B'],
    ['P', 'B', 'P', 'B', 'P', 'P', 'P', 'B', 'P', 'B', 'P', 'B', 'P', '.', 'P', 'B', 'P', 'B'],
    ['P', 'B', 'P', 'B', 'P', 'B', 'P', '.', 'P', 'B', 'P', '.', 'P', 'N', 'P', 'B', 'P', 'B'],
    ['P', '.', 'P', 'B', 'P', 'B', 'P', 'B', 'P', '.', 'P', 'P', 'P', 'B', 'P', 'B', 'P', 'B'],
    ['P', 'B', 'P', '.', 'P', 'B', 'P', '.', 'P', 'P', 'P', 'B', 'P', '.', 'P', 'B', 'P', '.'],
    ['P', '.', 'P', 'P', 'P', 'B', 'P', 'B', 'P', '.', 'P', 'B', 'P', 'B', 'P', '.', 'P', 'B'],
    ['P', 'B', 'P', 'P', 'P', 'B', 'P', '.', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B'],
    ['P', 'B', 'P', 'B', 'P', '.', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B'],
    ['P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B'],
    ['P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B'],
][::-1]

# Parity switch constructs (from infinite chess position strings)
# Knight enters from left on mod0, switches to mod1, then moves vertically
PARITY_SWITCH_DOWN = [
    ['P', 'B', 'P', 'B', 'P', 'B', 'P', 'B', 'P'],
    ['P', '.', 'P', '.', 'P', 'B', 'P', 'B', 'P'],
    ['P', '.', 'P', '.', 'P', '.', 'P', 'B', 'P'],
    ['P', 'B', '.', 'B', 'P', 'B', 'P', '.', 'P'],
    ['P', '.', 'P', '.', 'P', '.', 'P', 'B', 'P'],
][::-1]  # 9 wide, 5 tall

PARITY_SWITCH_UP = [
    ['P', 'B', 'P', 'B', 'P'],
    ['P', '.', 'B', '.', 'P'],
    ['P', 'B', '.', 'B', 'P'],
    ['P', '.', 'P', '.', 'P'],
    ['P', '.', 'P', '.', 'P'],
    ['P', '.', 'P', 'B', 'P'],
    ['P', 'B', 'P', '.', 'P'],
][::-1]  # 5 wide, 7 tall


@dataclass
class WireRoute:
    source_id: str
    target_id: str
    target_pin: int  # 0 for input A, 1 for input B
    source_y: int    # y-level of source gate's output
    target_y: int    # y-level of target gate's input


class LogicGate:
    # Connection point offsets relative to gate's bottom-left corner
    # These correspond to gaps in the nand_position template edges
    INPUT_A_OFFSET = (1, 6)   # left edge gap for input A
    INPUT_B_OFFSET = (1, 12)  # left edge gap for input B
    OUTPUT_OFFSET = (17, 5)   # right edge gap for output

    GATE_WIDTH = 18
    GATE_HEIGHT = 15

    def __init__(self, x, y, width, height, gate_type, input_coords, output_coord, position):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.gate_type = gate_type
        self.input_coords = input_coords  # list of (x, y) world-space tuples
        self.output_coord = output_coord  # (x, y) world-space tuple
        self.position = position

    @classmethod
    def nand(cls, x, y_top, num_inputs, num_outputs):
        assert num_inputs == 1 or num_inputs == 2
        assert num_outputs > 0
        position = nand_position
        width = cls.GATE_WIDTH
        height = cls.GATE_HEIGHT
        # y_top is the top edge; bottom-left is at (x, y_top - height)
        base_y = y_top - height

        input_coords = [
            (x + cls.INPUT_A_OFFSET[0], base_y + cls.INPUT_A_OFFSET[1]),
        ]
        if num_inputs == 2:
            input_coords.append(
                (x + cls.INPUT_B_OFFSET[0], base_y + cls.INPUT_B_OFFSET[1]),
            )
        output_coord = (x + cls.OUTPUT_OFFSET[0], base_y + cls.OUTPUT_OFFSET[1])

        return cls(x, y_top, width, height, 'NAND', input_coords, output_coord, position)

class ChessCircuit:
    """Manages a chess circuit with board state and gate locations."""

    def __init__(self, json_path, module_name='fn', stack_height=64):
        """Initialize with a netlist JSON file."""
        self.json_path = json_path
        self.module_name = module_name
        self.gate_layers = analyze_netlist(self.json_path, self.module_name, print_details=False)
        self.stack_height = stack_height  # vertical space for stacking gates
        self.pieces = {}  # (x, y) -> piece char (dict-based board)
        self.gates = {}   # gate_id -> LogicGate
        self.wire_routes_by_region = []  # list of (routes, x_start, x_end) per wire region
        self.add_wires()
        self.generate_circuit()

    def add_wires(self):
        """Insert wire passthrough nodes for signals that skip layers."""
        wire_idx = 0
        for i in range(len(self.gate_layers) - 1):
            next_layer_ids = {g['id'] for g in self.gate_layers[i+1]}
            for gate in self.gate_layers[i]:
                for output_idx in range(len(gate['outputs'])):
                    output = gate['outputs'][output_idx]
                    if output not in next_layer_ids:
                        wire_id = f'w{wire_idx}'
                        self.gate_layers[i+1] += [{
                            'id': wire_id,
                            'inputs': [gate['id']],
                            'outputs': [output]
                        }]
                        gate['outputs'][output_idx] = wire_id
                        wire_idx += 1

    def _set_piece(self, x, y, piece):
        """Set a piece on the board."""
        if piece != '.':
            self.pieces[(x, y)] = piece
        elif (x, y) in self.pieces:
            del self.pieces[(x, y)]

    def _stamp_template(self, template, world_x, world_y_bottom):
        """Stamp a 2D template onto the board at given bottom-left position."""
        for ty in range(len(template)):
            for tx in range(len(template[0])):
                piece = template[ty][tx]
                if piece != '.':
                    self._set_piece(world_x + tx, world_y_bottom + ty, piece)

    def _place_gate(self, gate_node, x_offset, y_top):
        """Place a single gate and return the LogicGate object."""
        gate = LogicGate.nand(x_offset, y_top, len(gate_node['inputs']), len(gate_node['outputs']))
        self.gates[gate_node['id']] = gate
        base_y = y_top - gate.height
        self._stamp_template(gate.position, x_offset, base_y)
        return gate

    def _find_source_output_y(self, source_id, current_layer_idx):
        """Find the y-coordinate of a source's output.
        Traces through wire nodes back to a gate, or assigns y for input ports.
        """
        # Direct gate in current layer
        if source_id in self.gates:
            return self.gates[source_id].output_coord[1]
        # Input port — assign a y-level based on port index
        if source_id.startswith('i'):
            port_num = int(source_id[1:])
            # Place inputs at the top of the stack, spaced by 4 rows (one wire height)
            return self.stack_height - 4 - port_num * 4
        # Wire node — trace back through the chain
        for layer in self.gate_layers:
            for node in layer:
                if node['id'] == source_id:
                    if node['inputs']:
                        return self._find_source_output_y(node['inputs'][0], current_layer_idx)
        return None

    def _compute_routes(self, current_layer, next_layer, layer_idx):
        """Compute wire routes between two adjacent gate columns."""
        routes = []
        # Build a map of what each node in the current layer outputs
        current_ids = {n['id'] for n in current_layer}

        for node in next_layer:
            if not node['id'].startswith('g'):
                continue
            target_gate = self.gates.get(node['id'])
            if not target_gate:
                continue

            for pin_idx, input_id in enumerate(node['inputs']):
                # Trace input_id back to find source y
                source_y = self._find_source_output_y(input_id, layer_idx)
                if source_y is None:
                    print(f"  WARNING: Could not find source y for {input_id} -> {node['id']}")
                    continue

                target_y = target_gate.input_coords[pin_idx][1] if pin_idx < len(target_gate.input_coords) else None
                if target_y is None:
                    continue

                routes.append(WireRoute(
                    source_id=input_id,
                    target_id=node['id'],
                    target_pin=pin_idx,
                    source_y=source_y,
                    target_y=target_y,
                ))

        return routes

    def _fill_solid_wall(self, x_start, x_end, y_start, y_end):
        """Fill a region with solid pawn/bishop walls."""
        for x in range(x_start, x_end):
            for y in range(y_start, y_end):
                if x % 2 == 0:
                    self._set_piece(x, y, 'P')
                else:
                    self._set_piece(x, y, 'B')

    def _carve_horizontal_wire(self, x_start, x_end, y_base):
        """Carve a horizontal wire at y_base (2 rows: y_base and y_base+1).
        Lower row (y_base): gaps at x where (x - x_start) % 4 == 1
        Upper row (y_base+1): gaps at x where (x - x_start) % 4 == 3
        Only carves gaps in odd-x (bishop) columns.
        """
        for x in range(x_start, x_end):
            if x % 2 == 1:  # bishop column
                rel_x = x - x_start
                if rel_x % 4 == 1:
                    self._set_piece(x, y_base, '.')  # lower gap
                elif rel_x % 4 == 3:
                    self._set_piece(x, y_base + 1, '.')  # upper gap

    def _place_wire_region(self, routes, wire_x_start):
        """Place the wire region between two gate columns.
        Returns the width of the wire region.
        """
        if not routes:
            # Minimum wire region: 4 columns of solid wall
            min_width = 4
            y_min = 0
            y_max = self.stack_height
            self._fill_solid_wall(wire_x_start, wire_x_start + min_width, y_min, y_max)
            return min_width

        # Determine if any wires need vertical transitions
        needs_vertical = any(r.source_y != r.target_y for r in routes)

        # Calculate wire region width
        if needs_vertical:
            # TODO: proper width calculation for parity switch constructs
            wire_width = 24  # placeholder: enough for horizontal + transitions
        else:
            wire_width = 8  # just horizontal wires

        # Round up to multiple of 4 for alignment
        wire_width = ((wire_width + 3) // 4) * 4

        wire_x_end = wire_x_start + wire_width

        # Fill entire region with solid walls first
        y_min = 0
        y_max = self.stack_height
        self._fill_solid_wall(wire_x_start, wire_x_end, y_min, y_max)

        # Detect crossings
        sorted_routes = sorted(routes, key=lambda r: r.source_y, reverse=True)
        for i in range(len(sorted_routes)):
            for j in range(i + 1, len(sorted_routes)):
                ri, rj = sorted_routes[i], sorted_routes[j]
                # Crossing: source order and target order disagree
                if (ri.source_y > rj.source_y and ri.target_y < rj.target_y) or \
                   (ri.source_y < rj.source_y and ri.target_y > rj.target_y):
                    print(f"  WARNING: Wire crossing detected: {ri.source_id}->{ri.target_id} crosses {rj.source_id}->{rj.target_id}")
                    # TODO: crossing resolution — underpass routing

        # Carve wires
        for route in routes:
            if route.source_y == route.target_y:
                # Straight horizontal wire
                self._carve_horizontal_wire(wire_x_start, wire_x_end, route.source_y)
            else:
                # Vertical transition needed
                # For now: carve horizontal at source_y, then at target_y
                # The parity switch constructs connect them (placeholder)
                self._carve_horizontal_wire(wire_x_start, wire_x_end, route.source_y)
                self._carve_horizontal_wire(wire_x_start, wire_x_end, route.target_y)

                # TODO: Place parity switch construct and vertical segment
                # Placeholder: stamp parity switch templates at midpoint
                mid_x = wire_x_start + wire_width // 2
                if route.target_y < route.source_y:
                    # Going down
                    print(f"  PLACEHOLDER: parity switch down at x={mid_x} for {route.source_id}->{route.target_id} (y={route.source_y}->{route.target_y})")
                else:
                    # Going up
                    print(f"  PLACEHOLDER: parity switch up at x={mid_x} for {route.source_id}->{route.target_id} (y={route.source_y}->{route.target_y})")

        self.wire_routes_by_region.append((routes, wire_x_start, wire_x_end))
        return wire_width

    def generate_circuit(self):
        """Generate the complete circuit layout iteratively:
        place gate column, then wire region, then next gate column, etc.
        """
        self.pieces = {}
        self.gates = {}
        self.wire_routes_by_region = []

        x_cursor = 0
        gate_width = LogicGate.GATE_WIDTH

        for layer_idx, layer in enumerate(self.gate_layers):
            # Phase A: Place gate column
            gates_in_layer = [n for n in layer if n['id'].startswith('g')]
            y_top = self.stack_height - 2

            for gate_node in gates_in_layer:
                assert y_top >= LogicGate.GATE_HEIGHT, \
                    f"Not enough vertical space for gate {gate_node['id']}, increase stack_height"
                self._place_gate(gate_node, x_cursor, y_top)
                y_top -= LogicGate.GATE_HEIGHT

            # Phase B: Wire region to next column
            if layer_idx < len(self.gate_layers) - 1:
                next_layer = self.gate_layers[layer_idx + 1]
                # Only compute routes if next layer has gates
                next_gates = [n for n in next_layer if n['id'].startswith('g')]
                if gates_in_layer and next_gates:
                    # We need to place next column's gates first to know their input coords
                    # Save x_cursor, tentatively place next gates, compute routes, then undo
                    next_x = x_cursor + gate_width  # tentative, will be adjusted
                    temp_y_top = self.stack_height - 2
                    for gn in next_gates:
                        temp_gate = LogicGate.nand(0, temp_y_top, len(gn['inputs']), len(gn['outputs']))
                        # Store with placeholder x — we just need relative y positions
                        self.gates[gn['id']] = temp_gate
                        temp_y_top -= LogicGate.GATE_HEIGHT

                    routes = self._compute_routes(layer, next_layer, layer_idx)

                    # Now fix the next gates' coords with actual x (after wire region)
                    # Remove temp gates — they'll be re-placed in the next iteration
                    for gn in next_gates:
                        del self.gates[gn['id']]

                    wire_x_start = x_cursor + gate_width
                    wire_width = self._place_wire_region(routes, wire_x_start)
                    x_cursor += gate_width + wire_width
                else:
                    # No wires needed (input/output layers)
                    if gates_in_layer:
                        x_cursor += gate_width
            else:
                if gates_in_layer:
                    x_cursor += gate_width

        # Compute board dimensions from placed pieces
        if self.pieces:
            self.width = max(x for x, y in self.pieces) + 1
            self.height = max(y for x, y in self.pieces) + 1
        else:
            self.width = 0
            self.height = 0

        # Convert dict to 2D array for compatibility
        self.board_state = [['.' for _ in range(self.width)] for _ in range(self.height)]
        for (x, y), piece in self.pieces.items():
            self.board_state[y][x] = piece

    def print_board_state(self, max_x=None, max_y=None):
        """Print a portion of the board state."""
        if max_x is None:
            max_x = min(self.width, 80)
        if max_y is None:
            max_y = min(self.height, 40)
        print("=" * 60)
        print("CHESS CIRCUIT BOARD STATE")
        print("=" * 60)
        print("Legend: P=Pawn, R=Rook, N=Knight, B=Bishop, Q=Queen, K=King, .=Empty")
        print()

        for y in range(max_y-1, -1, -1):
            row = ""
            for x in range(max_x):
                piece = self.pieces.get((x, y), '.')
                row += f" {piece} "
            print(f"{y:2d}: {row}")

        print("    ", end="")
        for x in range(max_x):
            print(f" {x:2d}", end="")
        print()

    def print_gate_summary(self):
        """Print a summary of all gates and their locations."""
        print("=" * 60)
        print("GATE LOCATIONS SUMMARY")
        print("=" * 60)

        for gate_id, gate in self.gates.items():
            print(f"Gate {gate_id} ({gate.gate_type}):")
            print(f"  Position: ({gate.x}, {gate.y})")
            print(f"  Inputs: {gate.input_coords}")
            print(f"  Output: {gate.output_coord}")
            print()

    def print_wire_summary(self):
        """Print a summary of wire routes."""
        print("=" * 60)
        print("WIRE ROUTES SUMMARY")
        print("=" * 60)
        for routes, x_start, x_end in self.wire_routes_by_region:
            print(f"Wire region x={x_start}..{x_end} ({x_end - x_start} cols):")
            for r in routes:
                direction = "straight" if r.source_y == r.target_y else \
                           f"{'up' if r.target_y > r.source_y else 'down'} ({abs(r.target_y - r.source_y)} rows)"
                print(f"  {r.source_id} -> {r.target_id}[pin{r.target_pin}]: y={r.source_y}->{r.target_y} ({direction})")
            print()

    def save_infinite_chess_format(self, output_file):
        """Save the board state in infinite chess format (v0;id,x,y;...)."""
        position_string = "v0;"
        for (x, y), piece in sorted(self.pieces.items()):
            if piece in piece_to_id:
                position_string += f"{piece_to_id[piece]},{x},{y};"

        with open(output_file, 'w') as f:
            f.write(position_string)

        print(f"Infinite chess position saved to {output_file}")

def main():
    """Main function for command line usage."""
    import sys
    
    if len(sys.argv) == 1:
        # Default to the old path
        json_path = '../synthesis/output/fn_nand.json'
        module_name = 'fn'
    else:
        json_path = sys.argv[1]
        module_name = sys.argv[2] if len(sys.argv) > 2 else 'fn'
    
    # Create the circuit
    circuit = ChessCircuit(json_path, module_name)
    
    # Print information
    circuit.print_board_state()
    circuit.print_gate_summary()
    circuit.print_wire_summary()
    
    # Save to output file in infinite chess format
    output_file = './output/fn_nand_chess.txt'
    circuit.save_infinite_chess_format(output_file)
        

if __name__ == "__main__":
    main() 
