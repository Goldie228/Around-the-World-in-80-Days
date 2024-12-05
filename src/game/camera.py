import pygame
import math
from pygame.math import Vector2
from settings import *


class Camera:
    """Handles camera movement and following the player"""

    def __init__(self):
        """Initialize camera with viewport dimensions"""
        # Camera viewport
        self.viewport = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Target position for smooth following
        self.target_pos = Vector2(0, 0)
        
        # Camera movement parameters
        self.smoothness = 0.2  # Lower = smoother
        self.damping = 1.5     # Higher = slower

    def _calculate_target_position(self, target: pygame.Rect) -> tuple[int, int]:
        """Calculate target position based on entity position
        
        Args:
            target: Entity to follow (usually player)
            
        Returns:
            Tuple of target x, y coordinates
        """
        # Center camera on target
        target_x = -target.centerx + WINDOW_WIDTH // 2
        target_y = -target.centery + WINDOW_HEIGHT // 2
        
        return target_x, target_y

    def _apply_smooth_movement(self) -> None:
        """Apply smooth movement towards target position"""
        # Calculate smooth movement factor
        smooth_factor = (1 - math.cos(math.pi * self.smoothness)) / self.damping
        
        # Update camera position with smooth interpolation
        self.viewport.x += (self.target_pos.x - self.viewport.x) * smooth_factor
        self.viewport.y += (self.target_pos.y - self.viewport.y) * smooth_factor

    def apply(self, entity: pygame.sprite.Sprite) -> pygame.Rect:
        """Apply camera offset to entity position
        
        Args:
            entity: Game entity to offset
            
        Returns:
            New rectangle with applied camera offset
        """
        return entity.rect.move(self.viewport.topleft)

    def update(self, dt: float, level: 'Level', target: 'Player') -> None:
        """Update camera position and render level
        
        Args:
            dt: Delta time
            level: Current game level
            target: Entity to follow (usually player)
        """
        # Update target position
        target_x, target_y = self._calculate_target_position(target.rect)
        self.target_pos.update(target_x, target_y)
        
        # Apply smooth camera movement
        self._apply_smooth_movement()
        
        # Update level camera target
        level.update_target(self.viewport)
        
        # Draw level with current camera position
        level.draw(dt, self.viewport.topleft)
