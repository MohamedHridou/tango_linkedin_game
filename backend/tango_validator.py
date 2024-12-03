# backend/tango_validator.py

def validate_tango_grid_with_hints(grid, hints):
    """
    Validates the entire grid with hints to ensure all Tango rules are followed.
    """
    return validate_tango_grid(grid) and validate_all_hints(grid, hints)

def validate_tango_grid(grid):
    """
    Validates the grid based on Tango's basic rules (symbol counts and adjacency).
    """
    return validate_rows_and_columns(grid) and validate_adjacency_full(grid)

def validate_rows_and_columns(grid):
    for i in range(6):
        row_symbols = [cell for cell in grid[i] if cell]
        col_symbols = [grid[j][i] for j in range(6) if grid[j][i]]
        
        if len(row_symbols) > 6 or len(col_symbols) > 6:
            return False
        if row_symbols.count('☀️') > 3 or row_symbols.count('🌑') > 3:
            return False
        if col_symbols.count('☀️') > 3 or col_symbols.count('🌑') > 3:
            return False
    return True

def validate_adjacency_full(grid):
    for row in range(6):
        for col in range(6):
            symbol = grid[row][col]
            if symbol:
                # Check horizontal adjacency
                if col < 5 and symbol == grid[row][col + 1]:
                    if col < 4 and symbol == grid[row][col + 2]:
                        return False
                # Check vertical adjacency
                if row < 5 and symbol == grid[row + 1][col]:
                    if row < 4 and symbol == grid[row + 2][col]:
                        return False
    return True

def validate_all_hints(grid, hints):
    # Validate horizontal hints
    for (row, col), hint in hints.get('horizontal', {}).items():
        if col >= 6 or row >= 6:
            return False
        current = grid[row][col]
        next_symbol = grid[row][col + 1] if (col + 1) < 6 else None
        if not current or not next_symbol:
            continue  # Cannot validate without both symbols
        if hint == '=' and current != next_symbol:
            return False
        if hint == 'X' and current == next_symbol:
            return False
    
    # Validate vertical hints
    for (row, col), hint in hints.get('vertical', {}).items():
        if row >= 6 or col >= 6:
            return False
        current = grid[row][col]
        next_symbol = grid[row + 1][col] if (row + 1) < 6 else None
        if not current or not next_symbol:
            continue  # Cannot validate without both symbols
        if hint == '=' and current != next_symbol:
            return False
        if hint == 'X' and current == next_symbol:
            return False
    
    return True

def validate_partial_grid_with_hints(grid, hints, row, col):
    """
    Validates the grid up to the current cell considering hints.
    """
    # Validate row and column counts
    row_symbols = [cell for cell in grid[row] if cell]
    col_symbols = [grid[r][col] for r in range(6) if grid[r][col]]
    
    if row_symbols.count('☀️') > 3 or row_symbols.count('🌑') > 3:
        return False
    if col_symbols.count('☀️') > 3 or col_symbols.count('🌑') > 3:
        return False
    
    # Validate adjacency
    symbol = grid[row][col]
    if symbol:
        # Check left two cells
        if col >= 2 and grid[row][col - 1] == symbol and grid[row][col - 2] == symbol:
            return False
        # Check above two cells
        if row >= 2 and grid[row - 1][col] == symbol and grid[row - 2][col] == symbol:
            return False
        # Check right two cells
        if col < 4 and grid[row][col + 1] == symbol and grid[row][col + 2] == symbol:
            return False
        # Check below two cells
        if row < 4 and grid[row + 1][col] == symbol and grid[row + 2][col] == symbol:
            return False
    
    # Validate hints related to current cell
    # Horizontal hint to the left
    if (row, col - 1) in hints.get('horizontal', {}):
        hint = hints['horizontal'][(row, col - 1)]
        left_symbol = grid[row][col - 1]
        if hint == '=' and symbol != left_symbol:
            return False
        if hint == 'X' and symbol == left_symbol:
            return False
    
    # Horizontal hint at current cell
    if (row, col) in hints.get('horizontal', {}):
        hint = hints['horizontal'][(row, col)]
        right_symbol = grid[row][col + 1] if (col + 1) < 6 else None
        if right_symbol:
            if hint == '=' and symbol != right_symbol:
                return False
            if hint == 'X' and symbol == right_symbol:
                return False
    
    # Vertical hint above
    if (row - 1, col) in hints.get('vertical', {}):
        hint = hints['vertical'][(row - 1, col)]
        above_symbol = grid[row - 1][col]
        if hint == '=' and symbol != above_symbol:
            return False
        if hint == 'X' and symbol == above_symbol:
            return False
    
    # Vertical hint at current cell
    if (row, col) in hints.get('vertical', {}):
        hint = hints['vertical'][(row, col)]
        below_symbol = grid[row + 1][col] if (row + 1) < 6 else None
        if below_symbol:
            if hint == '=' and symbol != below_symbol:
                return False
            if hint == 'X' and symbol == below_symbol:
                return False
    
    return True

def apply_trivial_rules(grid, hints):
    """
    Applies trivial rules to fill in cells deterministically.
    Returns True if any cell was filled, False otherwise.
    """
    changed = False
    for i in range(6):
        for j in range(6):
            if grid[i][j] is None:
                possible_symbols = get_possible_symbols(grid, hints, i, j)
                if len(possible_symbols) == 1:
                    grid[i][j] = possible_symbols[0]
                    changed = True
    return changed

def get_possible_symbols(grid, hints, row, col):
    """
    Returns a list of possible symbols for a cell based on trivial rules.
    """
    possible_symbols = ['☀️', '🌑']
    symbols_to_remove = []
    for symbol in possible_symbols:
        grid[row][col] = symbol
        if not validate_partial_grid_with_hints(grid, hints, row, col):
            symbols_to_remove.append(symbol)
        grid[row][col] = None
    for symbol in symbols_to_remove:
        possible_symbols.remove(symbol)
    return possible_symbols
