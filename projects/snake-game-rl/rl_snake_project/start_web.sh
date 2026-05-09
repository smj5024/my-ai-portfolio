#!/bin/bash
# Quick start script for Snake AI Web Visualization
# Usage: ./start_web.sh [model_path] [port] [speed]

MODEL_PATH=${1:-"./models/best_model.pth"}
PORT=${2:-5000}
SPEED=${3:-100}

echo "=================================================="
echo "🐍 Starting Snake AI Web Visualization"
echo "=================================================="
echo "Model: $MODEL_PATH"
echo "Port:  $PORT"
echo "Speed: ${SPEED}ms/step"
echo "=================================================="
echo ""
echo "📺 Open http://localhost:$PORT in your browser"
echo "Press Ctrl+C to stop"
echo ""

python3 play_web.py --model "$MODEL_PATH" --port "$PORT" --speed "$SPEED"
