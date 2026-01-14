# Project Dependencies

This document lists all dependencies used in the Manim_videos project.

## Core Animation Framework

### ManimGL (3Blue1Brown version)
- **manimgl** (1.7.2) - The main animation library
- **manimpango** (0.6.1) - Pango text rendering for Manim
- **moderngl** (5.12.0) - Modern OpenGL wrapper
- **moderngl-window** (3.1.1) - Window creation for ModernGL
- **glcontext** (3.0.0) - OpenGL context creation

## Python Scientific Stack

### Mathematics & Computation
- **numpy** (2.4.1) - Numerical computing
- **scipy** (1.17.0) - Scientific computing algorithms
- **sympy** (1.14.0) - Symbolic mathematics
- **mpmath** (1.3.0) - Multiprecision arithmetic

### Data Visualization
- **matplotlib** (3.10.8) - Plotting library
- **contourpy** (1.3.3) - Contour calculations for matplotlib
- **cycler** (0.12.1) - Color cycling for matplotlib
- **kiwisolver** (1.4.9) - Layout solver for matplotlib

## Graphics & Rendering

### 3D Graphics
- **PyOpenGL** (3.1.10) - OpenGL bindings
- **pyglm** (2.8.3) - OpenGL Mathematics library
- **pyglet** (2.1.12) - Cross-platform windowing and multimedia
- **isosurfaces** (0.1.2) - 3D isosurface rendering

### Image Processing
- **Pillow** (12.1.0) - Image manipulation
- **mapbox-earcut** (2.0.0) - Polygon triangulation

### Vector Graphics
- **svgelements** (1.9.6) - SVG parsing and manipulation
- **skia-pathops** (0.9.1) - Path operations
- **fonttools** (4.61.1) - Font manipulation

## Machine Learning & NLP (for Transformer demos)

### Deep Learning
- **torch** - PyTorch (required for transformer examples)
- **transformers** - HuggingFace Transformers library
  - GPT2Tokenizer
  - GPT2LMHeadModel
  - PreTrainedModel

### NLP Tools
- **tiktoken** (0.12.0) - OpenAI's tokenizer
- **gensim** (4.4.0) - Topic modeling and word embeddings
- **openai** - OpenAI API client (for GPT-3 examples)

## Development Tools

### Interactive Development
- **ipython** (9.9.0) - Enhanced Python shell
- **ipython-pygments-lexers** (1.1.1) - Syntax highlighting
- **jedi** (0.19.2) - Code completion
- **prompt-toolkit** (3.0.52) - Command line interface
- **matplotlib-inline** (0.2.1) - Inline plotting for IPython

### Terminal & UI
- **rich** (14.2.0) - Rich text and beautiful formatting
- **pygments** (2.19.2) - Syntax highlighting
- **markdown-it-py** (4.0.0) - Markdown parser
- **tqdm** (4.67.1) - Progress bars
- **screeninfo** (0.8.1) - Screen information

## Utilities

### File & Data Management
- **pyyaml** (6.0.3) - YAML parser (for config files)
- **appdirs** (1.4.4) - Application directories
- **diskcache** (5.6.3) - Disk caching
- **pyperclip** (1.11.0) - Clipboard operations

### Data Structures
- **addict** (2.4.0) - Dictionary subclass
- **colour** (0.1.5) - Color manipulation

### Network & HTTP
- **requests** (2.32.5) - HTTP library
- **urllib3** (2.6.3) - HTTP client
- **certifi** (2026.1.4) - SSL certificates
- **idna** (3.11) - Internationalized domain names
- **charset-normalizer** (3.4.4) - Character encoding detection

### Validation & Parsing
- **validators** (0.35.0) - Data validation
- **regex** (2025.11.3) - Regular expressions
- **pyparsing** (3.3.1) - Parser generator

## System Dependencies (non-Python)

### Video Encoding
- **ffmpeg** (8.0.1) - Video encoding and processing
  - Installed at: `~/bin/ffmpeg`

### LaTeX (optional, for mathematical typesetting)
- **LaTeX distribution** - Required for rendering mathematical formulas
  - Not currently installed (causes scenes using `Tex()` to fail)
  - Options: BasicTeX, tectonic, or full MacTeX

### Platform-Specific

#### macOS
- **pyobjc-core** (12.1) - Python-Objective-C bridge
- **pyobjc-framework-Cocoa** (12.1) - Cocoa framework bindings
- **Cython** (3.2.4) - C-extensions compiler

## Build & Packaging

- **setuptools** (80.9.0) - Package development
- **pip** (25.3) - Package installer
- **packaging** (25.0) - Core packaging utilities

## Supporting Libraries

- **six** (1.17.0) - Python 2/3 compatibility
- **python-dateutil** (2.9.0.post0) - Date utilities
- **traitlets** (5.14.3) - Configuration system
- **decorator** (5.2.1) - Decorator utilities
- **executing** (2.2.1) - Code execution inspection
- **asttokens** (3.0.1) - AST token utilities
- **stack-data** (0.6.3) - Stack frame inspection
- **pure-eval** (0.2.3) - Safe eval
- **parso** (0.8.5) - Python parser
- **ptyprocess** (0.7.0) - Pseudoterminal utilities
- **pexpect** (4.9.0) - Process automation
- **wcwidth** (0.2.14) - Terminal width calculation
- **mdurl** (0.1.2) - Markdown URL utilities
- **wrapt** (2.0.1) - Object proxying
- **smart-open** (7.5.0) - Streaming file I/O
- **pydub** (0.25.1) - Audio manipulation

## Installation

### Core Dependencies (Required)
```bash
# Install from virtual environment
source venv/bin/activate
pip install manimgl gensim tiktoken
```

### Optional Dependencies (for specific features)
```bash
# For transformer examples
pip install torch transformers openai

# For audio features
pip install pydub
```

### System Dependencies
```bash
# Install ffmpeg (already installed at ~/bin/ffmpeg)
# For LaTeX support (optional)
brew install --cask basictex  # Requires sudo
# OR
brew install tectonic  # No sudo required
```

## Environment Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Set PATH for ffmpeg
export PATH="$HOME/bin:/usr/bin:/bin:$PATH"

# Set PYTHONPATH for imports
export PYTHONPATH="/Users/test/Code/Manim_videos:$PYTHONPATH"
```

## Notes

- Python version: **3.12.12** (installed via Homebrew)
- Virtual environment: `venv/` (excluded from git)
- Output directory: `output/` (excluded from git)
- LaTeX is currently **not installed** - scenes using `Tex()` will fail
- The project uses the **3Blue1Brown fork** of Manim (manimgl), not ManimCommunity
