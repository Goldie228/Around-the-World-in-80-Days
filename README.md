# Around the World in 80 Days

A tile-based adventure game inspired by Jules Verne's classic novel, created in Python and Pygame. This is a college project and you shouldn't expect much from it.

## Features

- Custom game engine
- Built-in level editor
- Tile-based gameplay
- Dynamic camera system
- Custom animation system
- Save/Load functions (editor)

## Layer System

The game uses a layer-by-layer rendering system to create depth and visual interest. Layers are defined as follows:

- **Layer 1**:      Sky
- **Layer 2**:      Clouds
- **Layers 3-4**:   Background layers (infinite)
- **Layers 5-9**:   Background tiles
- **Layer 10**:     The main layer where the player, enemies, items, etc. are rendered.
- **Layers 11-13**: Foreground tiles
- **Layers 14-15**: Foreground Background

## Prerequisites

- Python 3.13.0 or higher
- pip (Python package installer)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/Goldie228/Around-the-World-in-80-Days.git
cd "Around-the-World-in-80-Days"
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the game:
```bash
python main.py
```

## Project Structure

```
around-the-world-80-days/
├── assets/               # Game assets
│   ├── editor/           # Editor-specific assets
│   │   ├── buttons/      # UI buttons
│   │   └── fonts/        # Custom fonts
│   ├── graphics/         # Game graphics
│   │   ├── colliders/    # Collision objects
│   │   ├── events/       # Event triggers
│   │   ├── player/       # Player animations
│   │   └── tiles/        # World tiles
│   └── sounds/           # Audio files
├── src/                  # Source code
│   ├── editor/           # Level editor
│   │   ├── editor.py     # Editor main class
│   │   ├── menu.py       # Editor menu system
│   │   └── settings.py   # Editor configuration
│   ├── game/             # Game logic
│   │   ├── level.py      # Level management
│   │   ├── camera.py     # Camera system
│   │   └── player.py     # Player mechanics
│   ├── save_manager.py   # Save/load system
│   └── settings.py       # Global settings
├── output/               # Output game .exe file
│   └── game.exe          # Executable file after packaging
│   main.py               # Entry point
├── LICENSE               # MIT license
├── README.md             # This file
└── requirements.txt      # Dependencies
```

## Development Setup

### Creating an executable file

1. Make sure you have auto-py-to-exe installed:
```bash
pip install auto-py-to-exe
```

2. Start the builder:
``bash
auto-py-to-exe
```

3. In the GUI:
   - Select `main.py` as the script location
   - Select `One Directory` as the output type
   - Select additional files from `assets/`.
   - Customise the icon and other settings
   - Click the ‘Convert .py to .exe’ button.

## Control

### Game
- **WASD** - move the player
- **Space** - player jump
- **F** - player attack

### Editor
- **Mouse** - Tile placement/selection
- **Ctrl+S** - Save Scene


## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgments

- Inspired by Jules Verne's "Around the World in 80 Days"
- Built with [Pygame](https://www.pygame.org/)
- Font: Press Start 2P by CodeMan38

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.
