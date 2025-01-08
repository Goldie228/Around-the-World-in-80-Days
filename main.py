import json
import pygame
import pygame.locals as pl
from pygame.image import load
from pygame.math import Vector2 as vector
from typing import Dict, Optional

from src.utils import resource_path
from src.settings import WINDOW_WIDTH, WINDOW_HEIGHT, EDITOR_MODE

if EDITOR_MODE:
    from src.editor.editor import Editor
else:
    from src.game.level import Level
    from src.game.player import Player
    from src.game.camera import Camera


class Main:
    """Main game class handling initialization and game loop"""
    
    def __init__(self):
        """Initialize game window and core components"""
        self.level = None
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
        levels_file_path = resource_path('assets/data/levels.json')  # Path to your JSON file
        levels_data = self.load_levels_from_json(levels_file_path)  # Load levels from JSON
        self.levels_paths: Dict[int, str] = levels_data['levels']  # Extract levels from JSON
        self.level: Optional[Level] = None
        self.player = Player()
        self.camera = Camera()
        
        try:
            self.change_level(0)
        except Exception as e:
            print(f"Error initializing game: {e}")
            
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

    @staticmethod
    def load_levels_from_json(file_path: str) -> Dict[int, str]:
        """Load levels from a JSON file"""
        with open(file_path, 'r') as file:
            return json.load(file)

    def change_level(self, index: int) -> None:
        """Change current level to specified index
        
        Args:
            index: Level index to load
        """
        index = str(index)

        if index not in self.levels_paths or not self.levels_paths[index]:
            print(f"Warning: No level found at index {index}")
            self.level = None  # Ensure level is set to None if not found
            return
        
        try:
            self.level = Level(self.levels_paths[index], self.switch, self.player)
        except Exception as e:
            print(f"Error changing level: {e}")
            self.level = None

    def _run_editor(self, dt: float) -> None:
        """Run editor mode update loop"""
        self.editor.run(dt)
        pygame.display.update()

    def _run_game(self, dt: float) -> None:
        """Run game mode update loop"""
        if self.level is not None:
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
