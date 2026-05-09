"""
Web-based Visualization for Snake RL Agent

This script creates a web interface to watch the trained agent play Snake.
It uses Flask to serve a web page with real-time game visualization.
Perfect for VSCode remote environments or headless servers.

Usage:
    python play_web.py --model ./models/best_model.pth --port 5000
    
Then open http://localhost:5000 in your browser.
"""

import argparse
import json
from flask import Flask, render_template_string, Response, jsonify
from flask_cors import CORS
import threading
import time
from env import SnakeGameNoRender, Direction, Point
from agent import DQNAgent


# Global variables for game state
game_state = {
    'snake': [],
    'food': {'x': 0, 'y': 0},
    'score': 0,
    'grid_width': 32,
    'grid_height': 24,
    'running': False,
    'episode': 0,
    'best_score': 0,
    'avg_score': 0.0,
    'total_games': 0,
    'total_score': 0
}


def run_game_agent(model_path, speed=100):
    """
    Run the agent in a separate thread and update global game state.
    
    Args:
        model_path (str): Path to trained model
        speed (int): Delay between steps in milliseconds
    """
    global game_state
    
    try:
        # Initialize environment (no render) - single food mode
        env = SnakeGameNoRender()
        
        # Get state size
        state_size = env._get_state().shape[0]
        
        # Initialize agent
        agent = DQNAgent(state_size=state_size, action_size=3)
        agent.load(model_path)
        agent.set_epsilon(0)  # Pure exploitation
        
        print(f"✓ Agent loaded from {model_path}")
        print("✓ Starting game simulation...")
        
        # Initialize game state with default values
        game_state['grid_width'] = env.grid_width
        game_state['grid_height'] = env.grid_height
        game_state['running'] = True
        game_state['snake'] = []
        game_state['food'] = {'x': 0, 'y': 0}
        game_state['score'] = 0
        game_state['episode'] = 0
        game_state['best_score'] = 0
        game_state['avg_score'] = 0.0
        game_state['total_games'] = 0
        game_state['total_score'] = 0
        
        print(f"✓ Grid size: {env.grid_width}x{env.grid_height}")
        print(f"✓ Initial stats - Episode: {game_state['episode']}, Best: {game_state['best_score']}, Avg: {game_state['avg_score']}")
        print("✓ Game thread started successfully")
        
        episode_count = 0
        while game_state['running']:
            state = env.reset()
            done = False
            
            # Update initial state after reset
            game_state['snake'] = [{'x': pt.x, 'y': pt.y} for pt in env.snake]
            game_state['food'] = {'x': env.food.x, 'y': env.food.y}
            game_state['score'] = env.score
            
            while not done and game_state['running']:
                # Select action
                action = agent.select_action(state, training=False)
                
                # Take action
                state, reward, done, info = env.step(action)
                
                # Update game state
                game_state['snake'] = [{'x': pt.x, 'y': pt.y} for pt in env.snake]
                game_state['food'] = {'x': env.food.x, 'y': env.food.y}  # Back to single food
                game_state['score'] = info.get('score', env.score)
                
                # Debug: log every 100 steps
                if env.steps % 100 == 0 and env.steps > 0:
                    print(f"⏱️  Step {env.steps}: Score={env.score}, Snake length={len(env.snake)}, Steps without food={env.steps_without_food}")
                
                # Sleep for visualization
                time.sleep(speed / 1000.0)
            
            if not game_state['running']:
                break
            
            # Update statistics
            episode_score = env.score
            episode_count += 1
            game_state['total_games'] += 1
            game_state['total_score'] += episode_score
            game_state['episode'] = game_state['total_games']
            
            if episode_score > game_state['best_score']:
                game_state['best_score'] = episode_score
            
            game_state['avg_score'] = game_state['total_score'] / game_state['total_games']
            
            print(f"📈 Episode {game_state['episode']} COMPLETED: Score = {episode_score}, "
                  f"Avg = {game_state['avg_score']:.2f}, Best = {game_state['best_score']}, "
                  f"Total Games = {game_state['total_games']}")
            
            # Small delay between episodes
            time.sleep(0.5)
        
        env.close()
        print("Game simulation stopped.")
        
    except Exception as e:
        print(f"✗ ERROR in game thread: {e}")
        import traceback
        traceback.print_exc()
        game_state['running'] = False


# HTML template for the web interface - using page refresh instead of API calls
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="2">
    <title>Snake AI - Web Visualization</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 30px;
            max-width: 1200px;
            width: 100%;
        }
        
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 20px;
            font-size: 2.5em;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 5px;
        }
        
        .stat-value {
            font-size: 1.8em;
            font-weight: bold;
        }
        
        #gameCanvas {
            display: block;
            margin: 0 auto;
            border: 3px solid #333;
            border-radius: 10px;
            background-color: #000;
        }
        
        .info {
            text-align: center;
            margin-top: 15px;
            color: #666;
            font-size: 0.9em;
        }
        
        .auto-refresh-notice {
            text-align: center;
            margin-top: 10px;
            padding: 10px;
            background: #fff3cd;
            border-radius: 5px;
            color: #856404;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐍 Snake AI Agent</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">Current Score</div>
                <div class="stat-value" id="score-val">{{ score }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Best Score</div>
                <div class="stat-value" id="best-score-val">{{ best_score }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Average Score</div>
                <div class="stat-value" id="avg-score-val">{{ avg_score }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Episodes</div>
                <div class="stat-value" id="episode-val">{{ episode }}</div>
            </div>
        </div>
        
        <canvas id="gameCanvas" width="640" height="480"></canvas>
        
        <div class="auto-refresh-notice">
            🔄 Page auto-refreshes every 2 seconds | Last update: {{ timestamp }}
        </div>
        
        <div class="info">
            <p>AI-powered Snake using Deep Q-Network (DQN)</p>
            <p>Game state is embedded directly in the page</p>
        </div>
    </div>
    
    <script>
        // Game state from server (embedded in HTML)
        const gameState = {{ game_state_json | safe }};
        
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        // Update stats from embedded state
        function updateStats() {
            if (gameState) {
                const scoreEl = document.getElementById('score-val');
                const bestScoreEl = document.getElementById('best-score-val');
                const avgScoreEl = document.getElementById('avg-score-val');
                const episodeEl = document.getElementById('episode-val');
                
                if (scoreEl) scoreEl.textContent = gameState.score;
                if (bestScoreEl) bestScoreEl.textContent = gameState.best_score;
                if (avgScoreEl) avgScoreEl.textContent = gameState.avg_score;
                if (episodeEl) episodeEl.textContent = gameState.episode;
            }
        }
        
        // Draw the game
        function drawGame() {
            if (!gameState) {
                console.error('No game state available');
                return;
            }
            
            // Clear canvas with natural gradient background
            const bgGradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
            bgGradient.addColorStop(0, '#1a1a2e');
            bgGradient.addColorStop(0.5, '#16213e');
            bgGradient.addColorStop(1, '#0f3460');
            ctx.fillStyle = bgGradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Add subtle texture (grass-like pattern)
            ctx.fillStyle = 'rgba(50, 100, 50, 0.05)';
            for (let i = 0; i < 100; i++) {
                const x = Math.random() * canvas.width;
                const y = Math.random() * canvas.height;
                const size = Math.random() * 3 + 1;
                ctx.fillRect(x, y, size, size);
            }
            
            const gridW = gameState.grid_width || 32;
            const gridH = gameState.grid_height || 24;
            const cellW = canvas.width / gridW;
            const cellH = canvas.height / gridH;
            
            // Draw snake with realistic snake-like appearance
            const snake = gameState.snake || [];
            
            if (snake.length > 0) {
                // Draw snake body as smooth connected circles
                for (let i = snake.length - 1; i >= 0; i--) {
                    const segment = snake[i];
                    const centerX = segment.x * cellW + cellW / 2;
                    const centerY = segment.y * cellH + cellH / 2;
                    
                    if (i === 0) {
                        // Head - larger and detailed
                        const headRadius = cellW / 2 + 2;
                        
                        // Head glow
                        ctx.shadowColor = '#00FF64';
                        ctx.shadowBlur = 15;
                        
                        // Main head
                        const headGradient = ctx.createRadialGradient(
                            centerX, centerY, 0,
                            centerX, centerY, headRadius
                        );
                        headGradient.addColorStop(0, '#00FF8C');
                        headGradient.addColorStop(0.7, '#00CC66');
                        headGradient.addColorStop(1, '#009944');
                        
                        ctx.fillStyle = headGradient;
                        ctx.beginPath();
                        ctx.arc(centerX, centerY, headRadius, 0, Math.PI * 2);
                        ctx.fill();
                        
                        // Reset shadow
                        ctx.shadowBlur = 0;
                        
                        // Eyes based on direction
                        const eyeOffset = cellW / 3;
                        const eyeRadius = cellW / 6;
                        const pupilRadius = cellW / 10;
                        
                        let eye1X, eye1Y, eye2X, eye2Y;
                        
                        // Calculate eye positions based on movement direction
                        if (snake.length > 1) {
                            const nextSegment = snake[1];
                            const dx = segment.x - nextSegment.x;
                            const dy = segment.y - nextSegment.y;
                            
                            // Determine direction
                            if (Math.abs(dx) > Math.abs(dy)) {
                                // Moving horizontally
                                if (dx > 0) { // Right
                                    eye1X = centerX + eyeOffset / 2;
                                    eye1Y = centerY - eyeOffset;
                                    eye2X = centerX + eyeOffset / 2;
                                    eye2Y = centerY + eyeOffset;
                                } else { // Left
                                    eye1X = centerX - eyeOffset / 2;
                                    eye1Y = centerY - eyeOffset;
                                    eye2X = centerX - eyeOffset / 2;
                                    eye2Y = centerY + eyeOffset;
                                }
                            } else {
                                // Moving vertically
                                if (dy > 0) { // Down
                                    eye1X = centerX - eyeOffset;
                                    eye1Y = centerY + eyeOffset / 2;
                                    eye2X = centerX + eyeOffset;
                                    eye2Y = centerY + eyeOffset / 2;
                                } else { // Up
                                    eye1X = centerX - eyeOffset;
                                    eye1Y = centerY - eyeOffset / 2;
                                    eye2X = centerX + eyeOffset;
                                    eye2Y = centerY - eyeOffset / 2;
                                }
                            }
                        } else {
                            // Default position
                            eye1X = centerX + eyeOffset / 2;
                            eye1Y = centerY - eyeOffset;
                            eye2X = centerX + eyeOffset / 2;
                            eye2Y = centerY + eyeOffset;
                        }
                        
                        // Eye whites
                        ctx.fillStyle = 'white';
                        ctx.beginPath();
                        ctx.arc(eye1X, eye1Y, eyeRadius, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.beginPath();
                        ctx.arc(eye2X, eye2Y, eyeRadius, 0, Math.PI * 2);
                        ctx.fill();
                        
                        // Pupils
                        ctx.fillStyle = 'black';
                        ctx.beginPath();
                        ctx.arc(eye1X, eye1Y, pupilRadius, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.beginPath();
                        ctx.arc(eye2X, eye2Y, pupilRadius, 0, Math.PI * 2);
                        ctx.fill();
                        
                        // Tongue (small red line sticking out)
                        ctx.strokeStyle = '#FF3232';
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        if (snake.length > 1) {
                            const nextSegment = snake[1];
                            const dx = segment.x - nextSegment.x;
                            const dy = segment.y - nextSegment.y;
                            
                            let tongueStartX, tongueStartY, tongueEndX, tongueEndY;
                            
                            if (Math.abs(dx) > Math.abs(dy)) {
                                if (dx > 0) { // Right
                                    tongueStartX = centerX + headRadius;
                                    tongueStartY = centerY;
                                    tongueEndX = centerX + headRadius + 8;
                                    tongueEndY = centerY;
                                } else { // Left
                                    tongueStartX = centerX - headRadius;
                                    tongueStartY = centerY;
                                    tongueEndX = centerX - headRadius - 8;
                                    tongueEndY = centerY;
                                }
                            } else {
                                if (dy > 0) { // Down
                                    tongueStartX = centerX;
                                    tongueStartY = centerY + headRadius;
                                    tongueEndX = centerX;
                                    tongueEndY = centerY + headRadius + 8;
                                } else { // Up
                                    tongueStartX = centerX;
                                    tongueStartY = centerY - headRadius;
                                    tongueEndX = centerX;
                                    tongueEndY = centerY - headRadius - 8;
                                }
                            }
                            ctx.moveTo(tongueStartX, tongueStartY);
                            ctx.lineTo(tongueEndX, tongueEndY);
                        }
                        ctx.stroke();
                        
                    } else {
                        // Body segments - gradient from light to dark
                        const progress = i / snake.length;
                        const greenValue = Math.floor(220 - progress * 120);
                        const bodyRadius = cellW / 2 - 1 - progress * 2;
                        
                        // Body segment with gradient
                        const bodyGradient = ctx.createRadialGradient(
                            centerX - bodyRadius / 3,
                            centerY - bodyRadius / 3,
                            0,
                            centerX,
                            centerY,
                            bodyRadius
                        );
                        bodyGradient.addColorStop(0, `rgb(100, ${greenValue + 40}, 100)`);
                        bodyGradient.addColorStop(0.5, `rgb(0, ${greenValue}, 50)`);
                        bodyGradient.addColorStop(1, `rgb(0, ${greenValue - 30}, 30)`);
                        
                        ctx.fillStyle = bodyGradient;
                        ctx.beginPath();
                        ctx.arc(centerX, centerY, Math.max(bodyRadius, 4), 0, Math.PI * 2);
                        ctx.fill();
                        
                        // Scale pattern (subtle texture)
                        if (i % 2 === 0) {
                            ctx.fillStyle = `rgba(255, 255, 255, 0.1)`;
                            ctx.beginPath();
                            ctx.arc(centerX, centerY, Math.max(bodyRadius * 0.6, 3), 0, Math.PI * 2);
                            ctx.fill();
                        }
                    }
                }
                
                // Draw smooth connections between segments
                ctx.strokeStyle = 'rgba(0, 180, 80, 0.3)';
                ctx.lineWidth = cellW * 0.6;
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';
                ctx.beginPath();
                ctx.moveTo(snake[0].x * cellW + cellW / 2, snake[0].y * cellH + cellH / 2);
                for (let i = 1; i < snake.length; i++) {
                    ctx.lineTo(snake[i].x * cellW + cellW / 2, snake[i].y * cellH + cellH / 2);
                }
                ctx.stroke();
            }
            
            // Draw food with beautiful effects
            const food = gameState.food || {x: 0, y: 0};
            
            // Glow effect
            ctx.shadowColor = '#FF3232';
            ctx.shadowBlur = 15;
            
            // Pulsing animation
            const pulse = Math.sin(Date.now() / 200) * 3;
            
            // Outer glow circle
            ctx.fillStyle = 'rgba(255, 50, 50, 0.3)';
            ctx.beginPath();
            ctx.arc(
                food.x * cellW + cellW / 2,
                food.y * cellH + cellH / 2,
                cellW / 2 + pulse,
                0,
                Math.PI * 2
            );
            ctx.fill();
            
            // Main food circle
            ctx.fillStyle = '#FF3232';
            ctx.beginPath();
            ctx.arc(
                food.x * cellW + cellW / 2,
                food.y * cellH + cellH / 2,
                cellW / 2 - 2,
                0,
                Math.PI * 2
            );
            ctx.fill();
            
            // Inner highlight
            ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
            ctx.beginPath();
            ctx.arc(
                food.x * cellW + cellW / 2 - 2,
                food.y * cellH + cellH / 2 - 2,
                cellW / 4,
                0,
                Math.PI * 2
            );
            ctx.fill();
            
            // Shine effect
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc(
                food.x * cellW + cellW / 2 - 3,
                food.y * cellH + cellH / 2 - 3,
                3,
                0,
                Math.PI * 2
            );
            ctx.fill();
            
            // Reset shadow
            ctx.shadowBlur = 0;
            
            console.log('✓ Game rendered - Score:', gameState.score);
        }
        
        // Draw when page loads
        window.addEventListener('load', () => {
            console.log('Page loaded with game state');
            updateStats();
            drawGame();
        });
    </script>
</body>
</html>
"""


# Flask application
app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    """Serve the main page with embedded game state."""
    # Debug logging
    print(f"📊 Rendering page - Score: {game_state.get('score', 0)}, "
          f"Episode: {game_state.get('episode', 0)}, "
          f"Best: {game_state.get('best_score', 0)}, "
          f"Avg: {game_state.get('avg_score', 0.0):.2f}")
    
    # Prepare game state as JSON string for embedding in HTML
    game_state_json = json.dumps({
        'snake': game_state.get('snake', []),
        'food': game_state.get('food', {'x': 0, 'y': 0}),  # Back to single food
        'score': game_state.get('score', 0),
        'grid_width': game_state.get('grid_width', 32),
        'grid_height': game_state.get('grid_height', 24),
        'episode': game_state.get('episode', 0),
        'best_score': game_state.get('best_score', 0),
        'avg_score': f"{game_state.get('avg_score', 0.0):.2f}"
    })
    
    # Render template with embedded data
    return render_template_string(
        HTML_TEMPLATE,
        score=game_state.get('score', 0),
        best_score=game_state.get('best_score', 0),
        avg_score=f"{game_state.get('avg_score', 0.0):.2f}",
        episode=game_state.get('episode', 0),
        game_state_json=game_state_json,
        timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
    )


@app.route('/data')
def get_data():
    """Simple data endpoint using common path name."""
    try:
        response_data = {
            'snake': game_state.get('snake', []),
            'food': game_state.get('food', {'x': 0, 'y': 0}),
            'score': game_state.get('score', 0),
            'grid_width': game_state.get('grid_width', 32),
            'grid_height': game_state.get('grid_height', 24),
            'running': game_state.get('running', False),
            'episode': game_state.get('episode', 0),
            'best_score': game_state.get('best_score', 0),
            'avg_score': float(game_state.get('avg_score', 0.0)),
            'total_games': game_state.get('total_games', 0),
            'total_score': game_state.get('total_score', 0)
        }
        return jsonify(response_data)
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/test')
def test_api():
    """Test endpoint to verify API is working."""
    return jsonify({
        'status': 'ok',
        'message': 'API is working!',
        'timestamp': time.time()
    })


@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': time.time()})


@app.route('/status')
def status_check():
    """Simple status endpoint without /api prefix."""
    return jsonify(game_state)


@app.route('/game_state')
def get_game_state_route():
    """API endpoint to get current game state - using simpler path for DSW compatibility."""
    try:
        # Ensure all required fields are present
        response_data = {
            'snake': game_state.get('snake', []),
            'food': game_state.get('food', {'x': 0, 'y': 0}),
            'score': game_state.get('score', 0),
            'grid_width': game_state.get('grid_width', 32),
            'grid_height': game_state.get('grid_height', 24),
            'running': game_state.get('running', False),
            'episode': game_state.get('episode', 0),
            'best_score': game_state.get('best_score', 0),
            'avg_score': float(game_state.get('avg_score', 0.0)),
            'total_games': game_state.get('total_games', 0),
            'total_score': game_state.get('total_score', 0)
        }
        # Debug logging
        print(f"✓ API called - Snake length: {len(response_data['snake'])}, Score: {response_data['score']}")
        return jsonify(response_data)
    except Exception as e:
        print(f"✗ Error in get_game_state: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/game_state')
def get_game_state_api():
    """API endpoint with /api prefix - kept for backward compatibility."""
    return get_game_state_route()


@app.route('/get_state', methods=['GET', 'POST'])
def get_state_post():
    """Endpoint that accepts both GET and POST for better gateway compatibility."""
    try:
        response_data = {
            'snake': game_state.get('snake', []),
            'food': game_state.get('food', {'x': 0, 'y': 0}),
            'score': game_state.get('score', 0),
            'grid_width': game_state.get('grid_width', 32),
            'grid_height': game_state.get('grid_height', 24),
            'running': game_state.get('running', False),
            'episode': game_state.get('episode', 0),
            'best_score': game_state.get('best_score', 0),
            'avg_score': float(game_state.get('avg_score', 0.0)),
            'total_games': game_state.get('total_games', 0),
            'total_score': game_state.get('total_score', 0)
        }
        return jsonify(response_data)
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset', methods=['POST'])
def reset_stats():
    """API endpoint to reset statistics."""
    global game_state
    game_state['episode'] = 0
    game_state['best_score'] = 0
    game_state['avg_score'] = 0
    game_state['total_games'] = 0
    game_state['total_score'] = 0
    return jsonify({'status': 'ok'})


@app.route('/stream')
def stream():
    """Server-Sent Events endpoint for real-time game state updates."""
    def generate():
        while True:
            try:
                # Prepare game state data
                data = {
                    'snake': game_state.get('snake', []),
                    'food': game_state.get('food', {'x': 0, 'y': 0}),
                    'score': game_state.get('score', 0),
                    'grid_width': game_state.get('grid_width', 32),
                    'grid_height': game_state.get('grid_height', 24),
                    'episode': game_state.get('episode', 0),
                    'best_score': game_state.get('best_score', 0),
                    'avg_score': float(game_state.get('avg_score', 0.0))
                }
                
                # Send as SSE format
                yield f"data: {json.dumps(data)}\n\n"
                
                # Wait before next update
                time.sleep(0.1)
            except GeneratorExit:
                break
            except Exception as e:
                print(f"SSE error: {e}")
                break
    
    return Response(generate(), mimetype='text/event-stream')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Watch Snake AI via Web Browser')
    parser.add_argument('--model', type=str, default='./models/best_model.pth',
                        help='Path to trained model (default: ./models/best_model.pth)')
    parser.add_argument('--speed', type=int, default=100,
                        help='Game speed in ms (lower = faster, default: 100)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Web server port (default: 5000)')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='Web server host (default: 0.0.0.0)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🐍 Snake AI - Web Visualization")
    print("=" * 60)
    print(f"Model: {args.model}")
    print(f"Speed: {args.speed}ms per step")
    print(f"Server: http://{args.host}:{args.port}")
    print("=" * 60)
    print("\n📺 Open the URL above in your browser to watch!")
    print("Press Ctrl+C to stop the server\n")
    
    # Start game simulation in a separate thread
    print("\n🔄 Starting game simulation thread...")
    game_thread = threading.Thread(
        target=run_game_agent,
        args=(args.model, args.speed),
        daemon=True
    )
    game_thread.start()
    print("✓ Game thread started\n")
    
    # Wait a moment for game thread to initialize
    time.sleep(1)
    
    # Start Flask server
    try:
        print(f"🚀 Starting Flask server on http://{args.host}:{args.port}")
        print(f"   - Host: {args.host}")
        print(f"   - Port: {args.port}")
        print(f"   - Debug: False")
        print(f"   - Use Reloader: False\n")
        app.run(host=args.host, port=args.port, debug=False, use_reloader=False)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n✗ ERROR: Port {args.port} is already in use!")
            print(f"   Try using a different port: ./start_web.sh ./models/best_model.pth 5001")
        else:
            print(f"\n✗ ERROR starting Flask server: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ ERROR starting Flask server: {e}")
        import traceback
        traceback.print_exc()
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping server...")
        game_state['running'] = False
        game_thread.join(timeout=2)
        print("✓ Server stopped.")


if __name__ == '__main__':
    main()
