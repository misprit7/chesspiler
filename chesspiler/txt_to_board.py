#!/usr/bin/env python3
"""
Convert an infinite chess editor .txt file (v0;id,x,y;...) to a Python 2D array (list of lists),
matching the format of ChessCircuit.board_state. Optionally clip to a coordinate box.

Usage:
  python txt_to_board.py input.txt [--min-x N] [--max-x N] [--min-y N] [--max-y N]

Prints Python code for the board_state array to stdout.
"""
import argparse
import sys

# Mapping from piece ID to symbol (expand as needed)
PIECE_ID_TO_SYMBOL = {
    0: 'P',  # White Pawn
    1: 'p',  # Black Pawn
    2: 'R',  # White Rook
    3: 'r',  # Black Rook
    4: 'N',  # White Knight
    5: 'n',  # Black Knight
    6: 'B',  # White Bishop
    7: 'b',  # Black Bishop
    8: 'Q',  # White Queen
    9: 'q',  # Black Queen
    10: 'K', # White King
    11: 'k', # Black King
    # Add more if needed
}

def parse_position_file(path):
    with open(path, 'r') as f:
        line = f.read().strip()
    if not line.startswith('v0;'):
        raise ValueError('File does not start with v0;')
    entries = line[3:].split(';')
    pieces = []
    for entry in entries:
        if not entry:
            continue
        parts = entry.split(',')
        if len(parts) != 3:
            continue
        try:
            pid = int(parts[0])
            x = int(parts[1])
            y = int(parts[2])
            pieces.append((pid, x, y))
        except Exception:
            continue
    return pieces

def parse_position_string(position_string):
    line = position_string.strip()
    if not line.startswith('v0;'):
        raise ValueError('Position string does not start with v0;')
    entries = line[3:].split(';')
    pieces = []
    for entry in entries:
        if not entry:
            continue
        parts = entry.split(',')
        if len(parts) != 3:
            continue
        try:
            pid = int(parts[0])
            x = int(parts[1])
            y = int(parts[2])
            pieces.append((pid, x, y))
        except Exception:
            continue
    return pieces

def get_bounds(pieces, min_x=None, max_x=None, min_y=None, max_y=None):
    xs = [x for _, x, _ in pieces]
    ys = [y for _, _, y in pieces]
    bx0 = min(xs) if min_x is None else min_x
    bx1 = max(xs) if max_x is None else max_x
    by0 = min(ys) if min_y is None else min_y
    by1 = max(ys) if max_y is None else max_y
    return bx0, bx1, by0, by1

def build_board_array(pieces, min_x, max_x, min_y, max_y):
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    board = [['.' for _ in range(width)] for _ in range(height)]  # board[y][x]
    for pid, x, y in pieces:
        if min_x <= x <= max_x and min_y <= y <= max_y:
            arr_x = x - min_x
            arr_y = y - min_y
            symbol = PIECE_ID_TO_SYMBOL.get(pid, '?')
            board[arr_y][arr_x] = symbol
    return board

def print_board_array(board):
    print('board_state = [')
    for row in reversed(board):
        print('    ' + repr(row) + ',')
    print('][::-1]')

def main():
    parser = argparse.ArgumentParser(description='Convert infinite chess .txt to Python board array.')
    parser.add_argument('input', nargs='?', help='Input .txt file (v0;id,x,y;...)')
    parser.add_argument('--board-string', type=str, default=None, help='Board state string (v0;id,x,y;...)')
    parser.add_argument('--min-x', type=int, default=None, help='Minimum x (inclusive)')
    parser.add_argument('--max-x', type=int, default=None, help='Maximum x (inclusive)')
    parser.add_argument('--min-y', type=int, default=None, help='Minimum y (inclusive)')
    parser.add_argument('--max-y', type=int, default=None, help='Maximum y (inclusive)')
    args = parser.parse_args()

    if args.board_string:
        pieces = parse_position_string(args.board_string)
    elif args.input:
        pieces = parse_position_file(args.input)
    else:
        print('Error: Must provide either an input file or --board-string.', file=sys.stderr)
        sys.exit(1)

    min_x, max_x, min_y, max_y = get_bounds(
        pieces, args.min_x, args.max_x, args.min_y, args.max_y
    )
    board = build_board_array(pieces, min_x, max_x, min_y, max_y)
    print_board_array(board)

if __name__ == '__main__':
    main() 