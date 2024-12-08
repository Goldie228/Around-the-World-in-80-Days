# Around the World in 80 Days

A tile-based adventure game inspired by Jules Verne's classic novel, built with Python and Pygame.

## Features

- Custom game engine
- Built-in level editor
- Tile-based gameplay
- Dynamic camera system
- Custom animation system
- Save/load functionality
- Configurable controls


## Layering System

The game utilizes a layered rendering system to create depth and visual interest. The layers are defined as follows:

- **Layer 1**: Sky
- **Layer 2**: Clouds
- **Layers 3-4**: Background layers
- **Layers 5-9**: Additional background layers
- **Layer 10**: Main layer where the player, enemies, items, etc. are rendered
- **Layers 11-13**: Foreground layers
- **Layers 14-15**: Foreground background (non-infinite), such as foliage, trees, etc.

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

### Required Dependencies

```bash
pip install pygame
pip install pandas
pip install auto-py-to-exe
```

### Building an Executable

1. Install auto-py-to-exe:
```bash
pip install auto-py-to-exe
```

2. Run the builder:
```bash
auto-py-to-exe
```

3. In the GUI:
   - Select `src/main.py` as the script location
   - Choose 'One Directory' as output type
   - Select additional files from `assets/`
   - Configure icon and other settings
   - Click 'Convert .py to .exe'

## Controls

- **WASD** - Player movement
- **Space** - Player jump

- **Mouse** - Tile placement/selection
- **Ctrl+S** - Save scene

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
