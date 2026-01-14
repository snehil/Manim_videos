# Test Scenes

This folder contains all test scenes for verifying ManimGL installation and testing new features.

## Available Test Scenes

- **test_yellow_circle.py** - Basic animation test with a yellow circle
- **simple_test.py** - Minimal scene for testing basic functionality

## Running Test Scenes

From the project root directory:

```bash
# Activate virtual environment
source venv/bin/activate

# Set up environment
export PATH="$HOME/bin:/usr/bin:/bin:$PATH"
export PYTHONPATH="/Users/test/Code/Manim_videos:$PYTHONPATH"

# Render a test scene
manimgl _2026/tests/test_yellow_circle.py YellowCircle -w
```

## Creating New Test Scenes

All new test scenes should be created in this folder. Use the existing scenes as templates.
