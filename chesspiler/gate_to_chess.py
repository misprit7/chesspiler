#!/usr/bin/env python3
"""
Convert synthesized NAND gates to chess positions.

This program takes the output from parse_gates.py and converts each gate
into a chess position representation as an infinite chess board where
each coordinate (x,y) is either occupied by a piece or empty.
"""

import json
from parse_gates import analyze_netlist

class LogicGate:
    def __init__(self, x, y, width, height, gate_type, input_coords, output_coord):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.gate_type = gate_type  # 'NAND' or 'NOT'
        self.input_coords = input_coords  # list of (x, y) tuples
        self.output_coord = output_coord  # (x, y) tuple

    @classmethod
    def nand(cls, x, y, num_outputs):
        input_coords = [(x, y), (x+2, y)]
        output_coord = (x+1, y+2)
        return cls(x, y, 3, 3, 'NAND', input_coords, output_coord)

    @classmethod
    def not_(cls, x, y, num_outputs):
        input_coords = [(x, y)]
        output_coord = (x+1, y+1)
        return cls(x, y, 2, 2, 'NOT', input_coords, output_coord)

class ChessCircuit:
    """Manages a chess circuit with board state and gate locations."""
    
    def __init__(self, json_path, module_name='fn', min_x=0, max_x=63, min_y=0, max_y=63):
        """Initialize with a netlist JSON file."""
        self.json_path = json_path
        self.module_name = module_name
        self.gate_layers = analyze_netlist(self.json_path, self.module_name, print_details=False)
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.width = self.max_x - self.min_x + 1
        self.height = self.max_y - self.min_y + 1
        self.board_state = [['.' for _ in range(self.height)] for _ in range(self.width)]
        self.gate_locations = {}
        self.generate_circuit()
    
    def get_nand_gate_position(self, gate_id, x_offset=0, y_offset=0):
        """Get chess position for a NAND gate.
        
        This is a placeholder implementation. Replace with actual chess piece
        positions that implement a NAND gate.
        
        Args:
            gate_id: The gate identifier
            x_offset: X coordinate offset for this gate
            y_offset: Y coordinate offset for this gate
        
        Returns:
            dict: Chess position with pieces at specific coordinates
        """
        # Placeholder NAND gate implementation
        # This should be replaced with actual chess piece positions
        # that implement a NAND gate when properly arranged
        
        pieces = {
            # Input A position
            (x_offset + 0, y_offset + 0): 'P',  # Pawn for input A
            # Input B position  
            (x_offset + 2, y_offset + 0): 'P',  # Pawn for input B
            # Output position
            (x_offset + 1, y_offset + 2): 'R',  # Rook for output
            # Internal pieces for NAND logic
            (x_offset + 1, y_offset + 1): 'N',  # Knight for internal logic
            (x_offset + 0, y_offset + 1): 'B',  # Bishop for internal logic
            (x_offset + 2, y_offset + 1): 'B',  # Bishop for internal logic
        }
        
        return {
            'gate_id': gate_id,
            'gate_type': 'NAND',
            'position': pieces,
            'bounds': {
                'min_x': x_offset,
                'max_x': x_offset + 2,
                'min_y': y_offset,
                'max_y': y_offset + 2
            }
        }
    
    def get_not_gate_position(self, gate_id, x_offset=0, y_offset=0):
        """Get chess position for a NOT gate.
        
        This is a placeholder implementation. Replace with actual chess piece
        positions that implement a NOT gate.
        
        Args:
            gate_id: The gate identifier
            x_offset: X coordinate offset for this gate
            y_offset: Y coordinate offset for this gate
        
        Returns:
            dict: Chess position with pieces at specific coordinates
        """
        # Placeholder NOT gate implementation
        pieces = {
            # Input position
            (x_offset + 0, y_offset + 0): 'P',  # Pawn for input
            # Output position
            (x_offset + 1, y_offset + 1): 'R',  # Rook for output
            # Internal piece for NOT logic
            (x_offset + 0, y_offset + 1): 'B',  # Bishop for internal logic
        }
        
        return {
            'gate_id': gate_id,
            'gate_type': 'NOT',
            'position': pieces,
            'bounds': {
                'min_x': x_offset,
                'max_x': x_offset + 1,
                'min_y': y_offset,
                'max_y': y_offset + 1
            }
        }
    
    def generate_circuit(self):
        """Generate the complete circuit layout."""
        x_spacing = 4
        y_spacing = 4
        self.gate_locations = {}
        # Reset board_state to empty
        self.board_state = [['.' for _ in range(self.height)] for _ in range(self.width)]
        y_offset = 0
        for depth, layer in enumerate(self.gate_layers):
            x_offset = 0
            for gate in layer:
                gate_id = gate['id']
                # Only place chess pieces for gates, not for input/output nodes
                if gate_id.startswith('g'):
                    chess_gate = self.get_nand_gate_position(gate_id, x_offset, y_offset)
                    self.gate_locations[gate_id] = {
                        'x_offset': x_offset,
                        'y_offset': y_offset,
                        'gate_type': chess_gate['gate_type'],
                        'depth': depth,
                        'inputs': gate['inputs'],
                        'outputs': gate['outputs']
                    }
                    for (x, y), piece in chess_gate['position'].items():
                        arr_x = x - self.min_x
                        arr_y = y - self.min_y
                        if 0 <= arr_x < self.width and 0 <= arr_y < self.height:
                            self.board_state[arr_x][arr_y] = piece
                    x_offset += x_spacing
            y_offset += y_spacing
    
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
                    piece = self.board_state[x][y]
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
        
        for gate_id, location in self.gate_locations.items():
            print(f"Gate {gate_id} ({location['gate_type']}):")
            print(f"  Position: ({location['x_offset']}, {location['y_offset']})")
            print(f"  Depth: {location['depth']}")
            print(f"  Inputs: {location['inputs']}")
            print(f"  Outputs: {location['outputs']}")
            print()
    
    def save_infinite_chess_format(self, output_file):
        """Save the board state in infinite chess format (v0;id,x,y;...)."""
        # Map pieces to template IDs based on editor.js
        piece_to_id = {
            'P': 0,  # White Pawn (assuming white for now)
            'R': 2,  # White Rook
            'N': 4,  # White Knight
            'B': 6,  # White Bishop
            'Q': 8,  # White Queen
            'K': 10, # White King
        }
        
        # Build the position string
        position_string = "v0;"
        for x in range(self.width):
            for y in range(self.height):
                piece = self.board_state[x][y]
                if piece in piece_to_id:
                    position_string += f"{piece_to_id[piece]},{x+self.min_x},{y+self.min_y};"
        
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