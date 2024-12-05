import os
import sys
import pygame
import pygame.locals as pl
from pygame.image import load
from pygame.math import Vector2 as vector
from typing import Dict, Optional

from settings import WINDOW_WIDTH, WINDOW_HEIGHT, EDITOR_MODE

if EDITOR_MODE:
    from editor.editor import Editor
else:
    from game.level import Level
    from game.player import Player
    from game.camera import Camera

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


class Main:
    """Main game class handling initialization and game loop"""
    
    def __init__(self):
        """Initialize game window and core components"""
        self._init_pygame()
        self._init_game_components()

    def _init_pygame(self) -> None:
        """Initialize Pygame and create window"""
        pygame.init()
        self.display_surface = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT), 
            pl.HWSURFACE | pl.DOUBLEBUF
        )
        self.clock = pygame.time.Clock()

    def _init_game_components(self) -> None:
        """Initialize game-specific components"""
        self.transition = Transition(self.switch)

        if EDITOR_MODE:
            self._init_editor()
        else:
            self._init_game()

    def _init_editor(self) -> None:
        """Initialize editor mode components"""
        self.editor = Editor()
        self._setup_cursor()

    def _init_game(self) -> None:
        """Initialize game mode components"""
        default_level = resource_path('assets/editor/saves/test4')
        self.levels_paths: Dict[int, str] = {
            0: default_level if os.path.exists(default_level) else None
        }
        self.level: Optional[Level] = None
        self.player = Player(30, 60)
        self.camera = Camera()
        
        try:
            self.change_level(0)
        except Exception as e:
            print(f"Error initializing game: {e}")
            # Handle initialization error (e.g., show error message, exit game)

    def _setup_cursor(self) -> None:
        """Setup custom mouse cursor"""
        cursor_path = resource_path('assets/graphics/cursors/mouse.png')
        cursor_surface = load(cursor_path).convert_alpha()
        cursor = pygame.cursors.Cursor((0, 0), cursor_surface)
        pygame.mouse.set_cursor(cursor)

    def switch(self, index: int = 0) -> None:
        """Switch to different level with transition"""
        self.transition.active = True
        self.change_level(index)

    def change_level(self, index: int) -> None:
        """Change current level to specified index
        
        Args:
            index: Level index to load
        """
        if index not in self.levels_paths or not self.levels_paths[index]:
            print(f"Warning: No level found at index {index}")
            return
        
        try:
            self.level = Level(self.levels_paths[index], self.switch, self.player)
        except Exception as e:
            print(f"Error changing level: {e}")
            # Handle level change error

    def _run_editor(self, dt: float) -> None:
        """Run editor mode update loop"""
        self.editor.run(dt)
        pygame.display.update()

    def _run_game(self, dt: float) -> None:
        """Run game mode update loop"""
        self.transition.display(dt)
        self.player.event_loop()
        self.player.update(self.level.collider_data.values(), dt)
        self.camera.update(dt, self.level, self.player)
        pygame.display.update()

    def run(self) -> None:
        """Main game loop"""
        if EDITOR_MODE:
            self.editor.start()
            self._run_editor_loop()
        else:
            pygame.display.set_caption('Around the World in 80 Days')
            self._run_game_loop()

    def _run_editor_loop(self) -> None:
        """Editor mode main loop"""
        while True:
            dt = self.clock.tick() * 0.001
            self._run_editor(dt)

    def _run_game_loop(self) -> None:
        """Game mode main loop"""
        while True:
            dt = self.clock.tick(60) * 0.001
            self._run_game(dt)


class Transition:
    """Handles level transition effects"""
    
    def __init__(self, toggle_callback):
        """Initialize transition effect"""
        self.display_surface = pygame.display.get_surface()
        self.toggle = toggle_callback
        self.active = False
        self._init_transition_parameters()

    def _init_transition_parameters(self) -> None:
        """Initialize transition effect parameters"""
        self.border_width = 0
        self.direction = 1
        self.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.radius = vector(self.center).magnitude()
        self.threshold = self.radius + 100

    def display(self, dt: float) -> None:
        """Update and display transition effect"""
        if not self.active:
            return

        self._update_transition(dt)
        self._draw_transition()

    def _update_transition(self, dt: float) -> None:
        """Update transition effect state"""
        self.border_width += 1000 * dt * self.direction
        
        if self.border_width >= self.threshold:
            self.direction = -1
            self.toggle()

        if self.border_width < 0:
            self._reset_transition()

    def _reset_transition(self) -> None:
        """Reset transition effect to initial state"""
        self.active = False
        self.border_width = 0
        self.direction = 1

    def _draw_transition(self) -> None:
        """Draw transition effect"""
        pygame.draw.circle(
            self.display_surface,
            'black',
            self.center,
            self.radius,
            int(self.border_width)
        )


if __name__ == '__main__':
    main = Main()
    main.run()
