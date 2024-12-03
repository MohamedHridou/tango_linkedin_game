# backend/tango_solver.py

from tango_validator import (
    validate_tango_grid_with_hints,
    validate_partial_grid_with_hints,
    apply_trivial_rules,
)

def solve_tango_puzzle(grid, hints, solutions=[], find_all=False, max_depth=None):
    """
    Solves a Tango puzzle considering the "=" and "X" constraints.
    """
    grid_copy = [row[:] for row in grid]
    changed = True
    while changed:
        changed = apply_trivial_rules(grid_copy, hints)
    empty_cell = find_empty_cell(grid_copy)
    if not empty_cell:
        if validate_tango_grid_with_hints(grid_copy, hints):
            solutions.append(grid_copy)
            return not find_all
        return False
    
    if max_depth is not None and max_depth < 0:
        return False  # Exceeded max depth
    
    row, col = empty_cell
    for symbol in ['☀️', '🌑']:
        grid_copy[row][col] = symbol
        if validate_partial_grid_with_hints(grid_copy, hints, row, col):
            if solve_tango_puzzle(
                grid_copy, hints, solutions, find_all, 
                max_depth - 1 if max_depth is not None else None
            ):
                if not find_all:
                    return True
        grid_copy[row][col] = None
    return False

def find_empty_cell(grid):
    for i in range(6):
        for j in range(6):
            if grid[i][j] is None:
                return (i, j)
    return None
