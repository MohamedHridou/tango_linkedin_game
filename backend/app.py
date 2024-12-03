# backend/app.py

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from tango_generator import generate_tango_puzzle
from tango_solver import solve_tango_puzzle
from tango_validator import validate_tango_grid_with_hints

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)  # Enable CORS for all routes

@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/generate_puzzle', methods=['GET'])
def api_generate_puzzle():
    difficulty = request.args.get('difficulty', 'medium')
    try:
        puzzle = generate_tango_puzzle(difficulty)
        # Convert hints keys to strings for JSON serialization
        hints_serializable = {
            'horizontal': {f"{k[0]},{k[1]}": v for k, v in puzzle['hints']['horizontal'].items()},
            'vertical': {f"{k[0]},{k[1]}": v for k, v in puzzle['hints']['vertical'].items()}
        }
        return jsonify({'status': 'success', 'grid': puzzle['grid'], 'hints': hints_serializable})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/solve_puzzle', methods=['POST'])
def api_solve_puzzle():
    data = request.get_json()
    grid = data.get('grid')
    hints = data.get('hints')
    if not grid or not hints:
        return jsonify({'status': 'error', 'message': 'Grid or hints data missing'}), 400
    # Convert hints keys back to tuples
    hints_converted = {
        'horizontal': {tuple(map(int, k.split(','))): v for k, v in hints.get('horizontal', {}).items()},
        'vertical': {tuple(map(int, k.split(','))): v for k, v in hints.get('vertical', {}).items()}
    }
    solutions = []
    grid_copy = [row[:] for row in grid]
    solve_tango_puzzle(grid_copy, hints_converted, solutions, find_all=False)
    if solutions:
        return jsonify({'status': 'success', 'solution': solutions[0]})
    else:
        return jsonify({'status': 'error', 'message': 'No solution found'}), 400

@app.route('/api/validate_puzzle', methods=['POST'])
def api_validate_puzzle():
    data = request.get_json()
    grid = data.get('grid')
    hints = data.get('hints')
    if not grid or not hints:
        return jsonify({'status': 'error', 'message': 'Grid or hints data missing'}), 400
    # Convert hints keys back to tuples
    hints_converted = {
        'horizontal': {tuple(map(int, k.split(','))): v for k, v in hints.get('horizontal', {}).items()},
        'vertical': {tuple(map(int, k.split(','))): v for k, v in hints.get('vertical', {}).items()}
    }
    is_valid = validate_tango_grid_with_hints(grid, hints_converted)
    return jsonify({'status': 'success', 'is_valid': is_valid})

if __name__ == '__main__':
    app.run(debug=True)
