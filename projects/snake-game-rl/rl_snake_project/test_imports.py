#!/usr/bin/env python3
"""
Simple test script to diagnose issues with the Snake RL project
"""

import sys
import os

print("=" * 60)
print("Python version:", sys.version)
print("Python executable:", sys.executable)
print("Current working directory:", os.getcwd())
print("=" * 60)

# Test imports
try:
    import numpy
    print("✓ numpy imported successfully, version:", numpy.__version__)
except Exception as e:
    print("✗ Failed to import numpy:", str(e))

try:
    import torch
    print("✓ torch imported successfully, version:", torch.__version__)
    print("  CUDA available:", torch.cuda.is_available())
except Exception as e:
    print("✗ Failed to import torch:", str(e))

try:
    import pygame
    print("✓ pygame imported successfully, version:", pygame.ver)
except Exception as e:
    print("✗ Failed to import pygame:", str(e))

try:
    import matplotlib
    print("✓ matplotlib imported successfully, version:", matplotlib.__version__)
except Exception as e:
    print("✗ Failed to import matplotlib:", str(e))

print("=" * 60)

# Try to import project modules
try:
    from env import SnakeGameNoRender
    print("✓ SnakeGameNoRender imported successfully")
    
    # Try to create environment
    env = SnakeGameNoRender()
    state = env.reset()
    print(f"✓ Environment created, state shape: {state.shape}")
    env.close()
except Exception as e:
    print("✗ Failed to import/create environment:")
    import traceback
    traceback.print_exc()

try:
    from agent import DQNAgent
    print("✓ DQNAgent imported successfully")
except Exception as e:
    print("✗ Failed to import DQNAgent:")
    import traceback
    traceback.print_exc()

print("=" * 60)
print("Diagnostic complete!")
