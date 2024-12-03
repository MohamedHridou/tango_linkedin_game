# backend/tango_generator.py

import random
from tango_solver import solve_tango_puzzle
from tango_validator import (
    validate_tango_grid_with_hints,
    validate_partial_grid_with_hints,
    apply_trivial_rules,
)

def generate_tango_puzzle(difficulty="medium"):
    """
    Generate a Tango puzzle with a unique solution.
    The puzzle includes minimal starting symbols and constraints to ensure deterministic solving.
    """
    max_attempts = 1000
    for attempt in range(max_attempts):
        # Step 1: Generate a complete valid grid
        full_grid = generate_full_grid()
        
        # Step 2: Remove cells and add minimal hints to ensure a unique, human-solvable puzzle
        puzzle = create_human_solvable_puzzle(full_grid, difficulty)
        
        if puzzle:
            return puzzle
    raise Exception("Failed to generate a human-solvable puzzle after multiple attempts.")

def generate_full_grid():
    """
    Generates a fully filled 6x6 grid adhering to Tango rules.
    """
    grid = [[None for _ in range(6)] for _ in range(6)]
    if not fill_grid(grid, 0, 0):
        raise Exception("Failed to generate a full grid.")
    return grid

def fill_grid(grid, row, col):
    """
    Recursively fills the grid ensuring Tango rules are followed.
    """
    if row == 6:
        return True
    next_row, next_col = (row, col + 1) if col < 5 else (row + 1, 0)
    
    symbols = ['☀️', '🌑']
    random.shuffle(symbols)
    for symbol in symbols:
        grid[row][col] = symbol
        if validate_partial_grid_with_hints(grid, {}, row, col):
            if fill_grid(grid, next_row, next_col):
                return True
        grid[row][col] = None
    return False

def create_human_solvable_puzzle(full_grid, difficulty):
    """
    Creates a puzzle that is human solvable by removing cells and adding hints.
    """
    # Start with an empty grid
    puzzle_grid = [[None for _ in range(6)] for _ in range(6)]
    hints = {'horizontal': {}, 'vertical': {}}
    
    # Copy a minimal number of starting symbols based on difficulty
    num_starting_symbols = {'easy': 14, 'medium': 10, 'hard': 8}
    num_symbols = num_starting_symbols.get(difficulty, 10)
    
    # Randomly select cells to keep
    cells = [(i, j) for i in range(6) for j in range(6)]
    random.shuffle(cells)
    for row, col in cells:
        if num_symbols == 0:
            break
        puzzle_grid[row][col] = full_grid[row][col]
        num_symbols -= 1
    
    # Step 3: Add minimal necessary hints
    if add_hints_for_human_solving(full_grid, puzzle_grid, hints):
        return {'grid': puzzle_grid, 'hints': hints}
    else:
        return None

def add_hints_for_human_solving(full_grid, puzzle_grid, hints):
    """
    Adds hints to the puzzle to ensure it's human solvable.
    """
    # Collect potential hints based on the full grid
    potential_hints = []
    for row in range(6):
        for col in range(6):
            if col < 5:
                symbol = full_grid[row][col]
                next_symbol = full_grid[row][col + 1]
                hint = '=' if symbol == next_symbol else 'X'
                potential_hints.append(('horizontal', (row, col), hint))
            if row < 5:
                symbol = full_grid[row][col]
                next_symbol = full_grid[row + 1][col]
                hint = '=' if symbol == next_symbol else 'X'
                potential_hints.append(('vertical', (row, col), hint))
    
    # Shuffle potential hints
    random.shuffle(potential_hints)
    
    # Try adding hints incrementally
    for direction, position, hint_value in potential_hints:
        hints_copy = {
            'horizontal': hints['horizontal'].copy(),
            'vertical': hints['vertical'].copy()
        }
        hints_copy[direction][position] = hint_value
        # Attempt to solve the puzzle using trivial rules and limited depth reasoning
        if is_puzzle_human_solvable(puzzle_grid, hints_copy):
            hints[direction][position] = hint_value
            # Check if the puzzle now has a unique solution
            solutions = []
            solve_tango_puzzle(puzzle_grid, hints, solutions, find_all=True, max_depth=3)
            if len(solutions) == 1:
                return True
    return False

def is_puzzle_human_solvable(puzzle_grid, hints):
    """
    Checks if the puzzle is human solvable using trivial rules and limited depth reasoning.
    """
    grid_copy = [row[:] for row in puzzle_grid]
    changed = True
    while changed:
        changed = apply_trivial_rules(grid_copy, hints)
    # If the grid is complete, it's solvable using trivial rules
    if all(all(cell is not None for cell in row) for row in grid_copy):
        return True
    # Else, attempt limited depth reasoning
    return attempt_limited_depth_reasoning(grid_copy, hints, max_depth=3)

def attempt_limited_depth_reasoning(grid, hints, max_depth):
    """
    Attempts to solve the puzzle using limited depth reasoning.
    """
    empty_cell = find_empty_cell(grid)
    if not empty_cell:
        return True  # Solved
    row, col = empty_cell
    for symbol in ['☀️', '🌑']:
        grid[row][col] = symbol
        if validate_partial_grid_with_hints(grid, hints, row, col):
            if max_depth > 0:
                if attempt_limited_depth_reasoning(grid, hints, max_depth - 1):
                    return True
            else:
                continue
        grid[row][col] = None
    return False

def find_empty_cell(grid):
    for i in range(6):
        for j in range(6):
            if grid[i][j] is None:
                return (i, j)
    return None
