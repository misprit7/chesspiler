#!/usr/bin/env python3
"""
Convert synthesized NAND gates to chess positions.

This program takes the output from parse_gates.py and converts each gate
into a chess position representation as an infinite chess board where
each coordinate (x,y) is either occupied by a piece or empty.
"""

import json
from parse_gates import analyze_netlist

class ChessCircuit:
    """Manages a chess circuit with board state and gate locations."""
    
    def __init__(self, json_path, module_name='fn'):
        """Initialize with a netlist JSON file."""
        self.json_path = json_path
        self.module_name = module_name
        self.gate_layers = analyze_netlist(self.json_path, self.module_name, print_details=False)
        self.board_state = {}
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
        self.board_state = {}
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
                        self.board_state[(x, y)] = piece
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
        for y in range(0, max_y)[::-1]:
            row = ""
            for x in range(max_x):
                piece = self.board_state.get((x, y), '.')  # Use negated Y coordinate
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
        for (x, y), piece in self.board_state.items():
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