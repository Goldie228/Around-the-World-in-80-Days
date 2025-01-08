"""
Editor-specific settings and configurations
"""
from typing import Dict, Optional, Tuple, Union
from pathlib import Path

# Core editor settings
TILE_SIZE: int = 64
MENU_MARGIN: int = 6
ANIMATION_SPEED: int = 4

# Asset paths
ASSETS_PATH = Path('assets')
GRAPHICS_PATH = ASSETS_PATH / 'graphics'
COLLIDERS_PATH = GRAPHICS_PATH / 'colliders'
EVENTS_PATH = GRAPHICS_PATH / 'events'
PLAYER_PATH = GRAPHICS_PATH / 'player'
TILES_PATH = GRAPHICS_PATH / 'tiles'
BACKGROUNDS_PATH = GRAPHICS_PATH / 'backgrounds'

# Editor data configuration
EditorDataType = Dict[int, Dict[str, Union[str, Optional[str]]]]

EDITOR_DATA: EditorDataType = {
    0: {
        'style': 'collider',
        'menu': 'collider',
        'menu_surf': str(COLLIDERS_PATH),
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
        'menu_surf': str(PLAYER_PATH / 'idle'),
        'graphics': str(PLAYER_PATH / 'idle')
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
        'style': 'npc',
        'menu': 'npc',
        'menu_surf': str(PLAYER_PATH / 'idle'),
        'graphics': str(PLAYER_PATH / 'idle')
    },
    8: {
        'style': 'terrain',
        'menu': 'boards',
        'menu_surf': str(TILES_PATH / 'boards'),
        'graphics': None
    },
    9: {
        'style': 'terrain',
        'menu': 'danger',
        'menu_surf': str(TILES_PATH / 'danger'),
        'graphics': None
    },
    10: {
        'style': 'terrain',
        'menu': 'details',
        'menu_surf': str(TILES_PATH / 'details'),
        'graphics': None
    },
    11: {
        'style': 'terrain',
        'menu': 'dirt',
        'menu_surf': str(TILES_PATH / 'dirt'),
        'graphics': None
    },
    12: {
        'style': 'terrain',
        'menu': 'dirty_grass',
        'menu_surf': str(TILES_PATH / 'dirty_grass'),
        'graphics': None
    },
    13: {
        'style': 'terrain',
        'menu': 'earth_elements',
        'menu_surf': str(TILES_PATH / 'earth_elements'),
        'graphics': None
    },
    14: {
        'style': 'terrain',
        'menu': 'earth_elements',
        'menu_surf': str(TILES_PATH / 'earth_elements'),
        'graphics': None
    },
    15: {
        'style': 'terrain',
        'menu': 'ground',
        'menu_surf': str(TILES_PATH / 'ground'),
        'graphics': None
    },
    16: {
        'style': 'terrain',
        'menu': 'mushrooms',
        'menu_surf': str(TILES_PATH / 'mushrooms'),
        'graphics': None
    },
    17: {
        'style': 'terrain',
        'menu': 'wood',
        'menu_surf': str(TILES_PATH / 'wood'),
        'graphics': None
    },
    18: {
        'style': 'terrain',
        'menu': 'background',
        'menu_surf': str(BACKGROUNDS_PATH),
        'graphics': None
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
