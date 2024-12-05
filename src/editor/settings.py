"""
Editor-specific settings and configurations
"""
from typing import Dict, Optional, Tuple, Union
from pathlib import Path

# Core editor settings
TILE_SIZE: int = 64
MENU_MARGIN: int = 6
ANIMATION_SPEED: int = 8

# Asset paths
ASSETS_PATH = Path('assets')
GRAPHICS_PATH = ASSETS_PATH / 'graphics'
COLIDERS_PATH = GRAPHICS_PATH / 'coliders'
EVENTS_PATH = GRAPHICS_PATH / 'events'
PLAYER_PATH = GRAPHICS_PATH / 'player'
TILES_PATH = GRAPHICS_PATH / 'tiles'

# Editor data configuration
EditorDataType = Dict[int, Dict[str, Union[str, Optional[str]]]]

EDITOR_DATA: EditorDataType = {
    0: {
        'style': 'colider',
        'menu': 'colider',
        'menu_surf': str(COLIDERS_PATH),
        'graphics': None
    },
    1: {
        'style': 'event',
        'menu': 'event',
        'menu_surf': str(EVENTS_PATH),
        'graphics': None
    },
    2: {
        'style': 'player',
        'menu': 'player',
        'menu_surf': str(PLAYER_PATH / 'idle_right'),
        'graphics': str(PLAYER_PATH / 'idle_right')
    },
    3: {
        'style': 'sky',
        'menu': 'sky',
        'menu_surf': str(GRAPHICS_PATH / 'clouds'),
        'graphics': None
    },
    4: {
        'style': 'terrain',
        'menu': 'terrain',
        'menu_surf': str(TILES_PATH / 'land'),
        'graphics': None
    },
    5: {
        'style': 'terrain',
        'menu': 'water',
        'menu_surf': str(TILES_PATH / 'water'),
        'graphics': str(TILES_PATH / 'water/animation')
    },
    6: {
        'style': 'terrain',
        'menu': 'water',
        'menu_surf': str(TILES_PATH / 'water'),
        'graphics': None
    },
    7: {
        'style': 'terrain',
        'menu': 'terrain1',
        'menu_surf': str(TILES_PATH / 'land'),
        'graphics': None
    },
    8: {
        'style': 'terrain',
        'menu': 'terrain2',
        'menu_surf': str(TILES_PATH / 'water'),
        'graphics': str(TILES_PATH / 'water/animation')
    },
    9: {
        'style': 'terrain',
        'menu': 'terrain3',
        'menu_surf': str(TILES_PATH / 'background'),
        'graphics': None
    },
    10: {
        'style': 'npc',
        'menu': 'npc',
        'menu_surf': str(PLAYER_PATH / 'idle_right'),
        'graphics': str(PLAYER_PATH / 'idle_right')
    },
}

# Camera movement configuration
CameraSpeedType = Dict[int, Tuple[int, int]]

CAMERA_SPEED_ON_LAYER: CameraSpeedType = {
    layer: (0, 0) for layer in range(15)
}

# Color definitions
class Colors:
    """Color constants for the editor"""
    SKY: str = '#ddc6a1'
    HORIZON: str = '#f5f1de'
    HORIZON_TOP: str = '#d1aa9d'
    BUTTON_BG: str = '#33323d'
    BUTTON_LINE: str = '#f5f1de'
    MENU_LINE: Tuple[int, int, int, int] = (21, 20, 26, 80)

# Export color constants
SKY_COLOR = Colors.SKY
HORIZON_COLOR = Colors.HORIZON
HORIZON_TOP_COLOR = Colors.HORIZON_TOP
BUTTON_BG_COLOR = Colors.BUTTON_BG
BUTTON_LINE_COLOR = Colors.BUTTON_LINE
MENU_LINE_COLOR = Colors.MENU_LINE
