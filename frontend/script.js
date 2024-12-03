// frontend/script.js

let grid = [];
let hints = { horizontal: {}, vertical: {} };
let solution = [];
let timerInterval;
let elapsedTime = 0;
let score = 0;
let difficulty = 'medium';
let gameCompleted = false;

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('new-game').addEventListener('click', newGame);
    document.getElementById('show-solution').addEventListener('click', showSolution);
    createGrid();
    newGame();
});

function createGrid() {
    const gridContainer = document.getElementById('grid');
    gridContainer.innerHTML = '';
    gridContainer.setAttribute('role', 'grid');
    for (let i = 0; i < 6; i++) {
        const rowDiv = document.createElement('div');
        rowDiv.classList.add('row');
        rowDiv.setAttribute('role', 'row');
        grid[i] = [];
        for (let j = 0; j < 6; j++) {
            const cellDiv = document.createElement('div');
            cellDiv.classList.add('cell', 'empty');
            cellDiv.dataset.row = i;
            cellDiv.dataset.col = j;
            cellDiv.setAttribute('role', 'gridcell');
            cellDiv.setAttribute('aria-label', `Row ${i + 1}, Column ${j + 1}`);
            cellDiv.setAttribute('tabindex', '0');
            cellDiv.addEventListener('click', cellClicked);
            cellDiv.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    cellClicked(e);
                }
            });
            rowDiv.appendChild(cellDiv);

            // Add horizontal hint
            if (j < 5) {
                const hHintDiv = document.createElement('div');
                hHintDiv.classList.add('h-hint');
                hHintDiv.setAttribute('aria-hidden', 'true');
                rowDiv.appendChild(hHintDiv);
            }

            grid[i][j] = null;
        }
        gridContainer.appendChild(rowDiv);

        // Add vertical hints
        if (i < 5) {
            const vHintRow = document.createElement('div');
            vHintRow.classList.add('v-hint-row');
            vHintRow.setAttribute('role', 'row');
            for (let j = 0; j < 6; j++) {
                const vHintDiv = document.createElement('div');
                vHintDiv.classList.add('v-hint');
                vHintDiv.setAttribute('aria-hidden', 'true');
                vHintRow.appendChild(vHintDiv);

                // Spacer for horizontal hints
                if (j < 5) {
                    const spacer = document.createElement('div');
                    spacer.classList.add('spacer');
                    spacer.setAttribute('aria-hidden', 'true');
                    vHintRow.appendChild(spacer);
                }
            }
            gridContainer.appendChild(vHintRow);
        }
    }
}

function cellClicked(event) {
    const row = parseInt(event.target.dataset.row);
    const col = parseInt(event.target.dataset.col);
    if (event.target.classList.contains('fixed') || event.target.classList.contains('solution')) {
        return;
    }
    const currentSymbol = event.target.textContent;
    if (currentSymbol === '') {
        event.target.textContent = '☀️';
        grid[row][col] = '☀️';
    } else if (currentSymbol === '☀️') {
        event.target.textContent = '🌑';
        grid[row][col] = '🌑';
    } else {
        event.target.textContent = '';
        grid[row][col] = null;
    }
    validateGrid();
}

function newGame() {
    difficulty = document.getElementById('difficulty').value;
    fetch(`/api/generate_puzzle?difficulty=${difficulty}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                loadPuzzle(data.grid, data.hints);
                solution = [];
                resetTimer();
                startTimer();
                score = 0;
                updateScore();
                gameCompleted = false;
            } else {
                alert('Error generating puzzle: ' + data.message);
            }
        });
}

function loadPuzzle(puzzleGrid, puzzleHints) {
    hints = puzzleHints;
    for (let i = 0; i < 6; i++) {
        for (let j = 0; j < 6; j++) {
            const cellDiv = document.querySelector(`.cell[data-row="${i}"][data-col="${j}"]`);
            const value = puzzleGrid[i][j];
            grid[i][j] = value;
            if (value) {
                cellDiv.textContent = value;
                cellDiv.classList.add('fixed');
                cellDiv.classList.remove('empty');
            } else {
                cellDiv.textContent = '';
                cellDiv.classList.remove('fixed');
                cellDiv.classList.add('empty');
            }
        }
    }
    renderHints();
    highlightInvalidCells();
}

function renderHints() {
    // Clear existing hints
    document.querySelectorAll('.h-hint').forEach(hHint => {
        hHint.textContent = '';
    });
    document.querySelectorAll('.v-hint').forEach(vHint => {
        vHint.textContent = '';
    });

    // Render horizontal hints
    for (let key in hints.horizontal) {
        const [row, col] = key.split(',').map(Number);
        const hintValue = hints.horizontal[key];
        const hHintDiv = document.querySelector(`.row:nth-child(${row + 1}) .h-hint:nth-child(${col * 2 + 2})`);
        hHintDiv.textContent = hintValue;
    }

    // Render vertical hints
    for (let key in hints.vertical) {
        const [row, col] = key.split(',').map(Number);
        const hintValue = hints.vertical[key];
        const vHintRow = document.querySelector(`.v-hint-row:nth-child(${row * 2 + 2})`);
        const vHintDiv = vHintRow.querySelector(`.v-hint:nth-child(${col * 2 + 1})`);
        vHintDiv.textContent = hintValue;
    }
}

function validateGrid() {
    fetch('/api/validate_puzzle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ grid: grid, hints: hints })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                if (data.is_valid && isGridFull() && !gameCompleted) {
                    gameCompleted = true;
                    clearInterval(timerInterval);
                    score = calculateScore(elapsedTime, difficulty);
                    updateScore();
                    alert(`Congratulations! You solved the puzzle in ${formatTime(elapsedTime)}.\nYour score: ${score}`);
                }
                highlightInvalidCells();
            } else {
                console.error('Validation error:', data.message);
            }
        });
}

function isGridFull() {
    for (let row of grid) {
        for (let cell of row) {
            if (!cell) {
                return false;
            }
        }
    }
    return true;
}

function showSolution() {
    if (solution.length > 0) {
        displaySolution(solution);
    } else {
        fetch('/api/solve_puzzle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ grid: grid, hints: hints })
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    solution = data.solution;
                    displaySolution(solution);
                } else {
                    alert('No solution found or error: ' + data.message);
                }
            });
    }
}

function displaySolution(solutionGrid) {
    for (let i = 0; i < 6; i++) {
        for (let j = 0; j < 6; j++) {
            const cellDiv = document.querySelector(`.cell[data-row="${i}"][data-col="${j}"]`);
            const value = solutionGrid[i][j];
            cellDiv.textContent = value;
            grid[i][j] = value;
            if (!cellDiv.classList.contains('fixed')) {
                cellDiv.classList.add('solution');
                cellDiv.classList.remove('empty');
            }
        }
    }
    highlightInvalidCells();
}

function highlightInvalidCells() {
    // Remove previous invalid highlights
    document.querySelectorAll('.cell').forEach(cell => {
        cell.classList.remove('invalid');
    });

    // Perform client-side validation
    let invalidCells = getInvalidCells();
    invalidCells.forEach(({ row, col }) => {
        const cellDiv = document.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
        cellDiv.classList.add('invalid');
    });
}

function getInvalidCells() {
    let invalidCells = [];

    // Check rows and columns for symbol counts
    for (let i = 0; i < 6; i++) {
        let rowSymbols = {};
        let colSymbols = {};
        for (let j = 0; j < 6; j++) {
            let rowSymbol = grid[i][j];
            let colSymbol = grid[j][i];

            if (rowSymbol) {
                rowSymbols[rowSymbol] = (rowSymbols[rowSymbol] || 0) + 1;
                if (rowSymbols[rowSymbol] > 3) {
                    invalidCells.push({ row: i, col: j });
                }
            }
            if (colSymbol) {
                colSymbols[colSymbol] = (colSymbols[colSymbol] || 0) + 1;
                if (colSymbols[colSymbol] > 3) {
                    invalidCells.push({ row: j, col: i });
                }
            }
        }
    }

    // Check adjacency rules
    for (let i = 0; i < 6; i++) {
        for (let j = 0; j < 6; j++) {
            let symbol = grid[i][j];
            if (symbol) {
                // Horizontal adjacency
                if (j < 4 && symbol === grid[i][j + 1] && symbol === grid[i][j + 2]) {
                    invalidCells.push({ row: i, col: j }, { row: i, col: j + 1 }, { row: i, col: j + 2 });
                }
                // Vertical adjacency
                if (i < 4 && symbol === grid[i + 1][j] && symbol === grid[i + 2][j]) {
                    invalidCells.push({ row: i, col: j }, { row: i + 1, col: j }, { row: i + 2, col: j });
                }
            }
        }
    }

    // Check "=" and "X" constraints
    for (let key in hints.horizontal) {
        const [row, col] = key.split(',').map(Number);
        const hint = hints.horizontal[key];
        const current = grid[row][col];
        const next = grid[row][col + 1];
        if (current && next) {
            if (hint === '=' && current !== next) {
                invalidCells.push({ row, col }, { row, col: col + 1 });
            }
            if (hint === 'X' && current === next) {
                invalidCells.push({ row, col }, { row, col: col + 1 });
            }
        }
    }
    for (let key in hints.vertical) {
        const [row, col] = key.split(',').map(Number);
        const hint = hints.vertical[key];
        const current = grid[row][col];
        const next = grid[row + 1][col];
        if (current && next) {
            if (hint === '=' && current !== next) {
                invalidCells.push({ row, col }, { row: row + 1, col });
            }
            if (hint === 'X' && current === next) {
                invalidCells.push({ row, col }, { row: row + 1, col });
            }
        }
    }

    // Remove duplicates
    invalidCells = invalidCells.filter((cell, index, self) =>
        index === self.findIndex((c) => c.row === cell.row && c.col === cell.col)
    );

    return invalidCells;
}

function startTimer() {
    elapsedTime = 0;
    clearInterval(timerInterval);
    document.getElementById('timer').textContent = `Time: 00:00`;
    timerInterval = setInterval(() => {
        elapsedTime++;
        document.getElementById('timer').textContent = `Time: ${formatTime(elapsedTime)}`;
    }, 1000);
}

function resetTimer() {
    clearInterval(timerInterval);
    elapsedTime = 0;
    document.getElementById('timer').textContent = `Time: 00:00`;
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
    const secs = (seconds % 60).toString().padStart(2, '0');
    return `${mins}:${secs}`;
}

function calculateScore(time, difficulty) {
    const difficultyMultiplier = { 'easy': 1, 'medium': 1.5, 'hard': 2 };
    let baseScore = 1000 - time * 10;
    if (baseScore < 0) baseScore = 0;
    return Math.floor(baseScore * difficultyMultiplier[difficulty]);
}

function updateScore() {
    document.getElementById('score').textContent = `Score: ${score}`;
}
