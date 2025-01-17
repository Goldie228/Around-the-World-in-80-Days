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
PLAYER_IMAGE_WIDTH: int = 103
PLAYER_IMAGE_HEIGHT: int = 103
PLAYER_WIDTH: int = 32
PLAYER_HEIGHT: int = 103
PLAYER_ANIMATION_SPEED: int = 6
PLAYER_IMAGE_INDENT: int = 37
