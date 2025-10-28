#!/usr/bin/env python3
"""
Convert synthesized NAND gates to chess positions.

This program takes the output from parse_gates.py and converts each gate
into a chess position representation as an infinite chess board where
each coordinate (x,y) is either occupied by a piece or empty.
"""

import json
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

class LogicGate:
    def __init__(self, x, y, width, height, gate_type, input_coords, output_coord, position):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.gate_type = gate_type  # 'NAND' or 'NOT'
        self.input_coords = input_coords  # list of (x, y) tuples
        self.output_coord = output_coord  # (x, y) tuple
        self.position = position

    @classmethod
    def nand(cls, x, y, num_inputs, num_outputs):
        assert num_inputs == 1 or num_inputs == 2
        assert num_outputs > 0
        # TODO: Add special handling for 1 input (i.e. NOT gate)
        position = nand_position
        input_coords = [(x, y), (x+2, y)]
        output_coord = (x+1, y+2)
        return cls(x, y, len(position[0]), len(position), 'NAND', input_coords, output_coord, position)

    # @classmethod
    # def not_(cls, x, y, num_outputs):
    #     position = nand_position
    #     input_coords = [(x, y)]
    #     output_coord = (x+1, y+1)
    #     # TODO: change to separate not gate (probably just add an extra knight and move pawn)
    #     return cls(x, y, len(position[0]), len(position), 'NOT', input_coords, output_coord, position)
    

class ChessCircuit:
    """Manages a chess circuit with board state and gate locations."""
    
    def __init__(self, json_path, module_name='fn', width=512, height=64):
        """Initialize with a netlist JSON file."""
        self.json_path = json_path
        self.module_name = module_name
        self.gate_layers = analyze_netlist(self.json_path, self.module_name, print_details=False)
        self.width = width
        self.height = height
        self.board_state = [['.' for _ in range(self.width)] for _ in range(self.height)]  # board_state[y][x]
        self.gates = {}
        self.generate_circuit()
    
    def generate_circuit(self):
        """Generate the complete circuit layout."""
        self.gate_locations = {}
        
        # Reset board_state to empty
        self.board_state = [['.' for _ in range(self.width)] for _ in range(self.height)]
        x_offset = 0
        for depth, layer in enumerate(self.gate_layers):
            y_offset = self.height - 2
            for gate in layer:
                assert y_offset >= 0, "y coordinate < 0, probably this means your circuit is too big and you should increase max height"

                gate_id = gate['id']

                # Only place chess pieces for gates, not for input/output nodes
                if gate_id.startswith('g'):
                    # print(gate)
                    # assert 0
                    chess_gate = LogicGate.nand(x_offset, y_offset, len(gate['inputs']), len(gate['outputs']))
                    self.gates[gate_id] = chess_gate
                    for gate_y in range(chess_gate.height):
                        for gate_x in range(chess_gate.width):
                            piece = chess_gate.position[gate_y][gate_x]
                            if piece != '.':
                                world_x = x_offset + gate_x
                                # By convention the offset is for top left
                                world_y = y_offset + gate_y - chess_gate.height
                                assert 0 <= world_x < self.width and 0 <= world_y < self.height, "Attempting to assign outside of board area"
                                self.board_state[world_y][world_x] = piece

                    y_offset -= chess_gate.height
            x_offset += 35
    
    def print_board_state(self, max_x=20, max_y=20):
        """Print a portion of the board state."""
        print("=" * 60)
        print("CHESS CIRCUIT BOARD STATE")
        print("=" * 60)
        print("Legend: P=Pawn, R=Rook, N=Knight, B=Bishop, Q=Queen, K=King, .=Empty")
        print()
        
        # Print the board portion (Y coordinates negated to match infinite chess format)
        for y in range(max_y-1, -1, -1):
            row = ""
            for x in range(max_x):
                if 0 <= x < self.width and 0 <= y < self.height:
                    piece = self.board_state[y][x]
                else:
                    piece = '.'
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
            print()
    
    def save_infinite_chess_format(self, output_file):
        """Save the board state in infinite chess format (v0;id,x,y;...)."""
        
        # Build the position string
        position_string = "v0;"
        for y in range(self.height):
            for x in range(self.width):
                piece = self.board_state[y][x]
                if piece in piece_to_id:
                    position_string += f"{piece_to_id[piece]},{x},{y};"
        
        # Save to file
        with open(output_file, 'w') as f:
            f.write(position_string)
        
        print(f"Infinite chess position saved to {output_file}")
        print(f"Position string: {position_string}")

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
    
    try:
        # Create the circuit
        circuit = ChessCircuit(json_path, module_name)
        
        # Print information
        circuit.print_board_state()
        circuit.print_gate_summary()
        
        # Save to output file in infinite chess format
        output_file = './output/fn_nand_chess.txt'
        circuit.save_infinite_chess_format(output_file)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
