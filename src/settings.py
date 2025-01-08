"""
Global application settings
"""
from src.utils import resource_path

# Window dimensions
WINDOW_WIDTH: int = 1280
WINDOW_HEIGHT: int = 720

# Application mode
EDITOR_MODE: bool = False

# Player settings
PLAYER_PATH: str = resource_path('assets/graphics/player')
PLAYER_WIDTH: int = 64
PLAYER_HEIGHT: int = 100
PLAYER_ANIMATION_SPEED: int = 15
