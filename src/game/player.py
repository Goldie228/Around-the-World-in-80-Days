import pygame
import sys
from pygame.math import Vector2


class Player:
    """Represents the player character in the game"""

    def __init__(self, width: int, height: int):
        """Initialize player with dimensions and physics properties"""
        # Physical properties
        self.rect = pygame.Rect(0, 0, width, height)
        self.direction = Vector2(0, 0)
        
        # Movement parameters
        self.speed = 6
        self.sprint_multiplier = 1.5
        self.jump_power = 5
        
        # Physics parameters
        self.gravity = 0.1
        self.terminal_velocity = 10
        self.on_ground = False
        
        # Level width
        self.start_width = 0
        self.end_width = 0

    def set_coords(self, origin: Vector2) -> None:
        """Set player position relative to origin point"""
        self.rect = self.rect.move(origin.x, origin.y)

    def event_loop(self) -> None:
        """Handle player input events"""
        self._handle_quit_event()
        self._handle_movement_input()

    def _handle_quit_event(self) -> None:
        """Handle game quit event"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def _handle_movement_input(self) -> None:
        """Process keyboard input for player movement"""
        keys = pygame.key.get_pressed()
        
        # Reset horizontal velocity
        self.direction.x = 0
        
        # Horizontal movement
        self._process_horizontal_movement(keys)
        
        # Jump
        self._process_jump(keys)

    def _process_horizontal_movement(self, keys) -> None:
        """Handle horizontal movement based on keyboard input"""
        # Left movement
        if (keys[pygame.K_a] and not keys[pygame.K_d]):
            if self.rect.left > self.start_width:
                self.direction.x = -1
            else:
                self.direction.x = 0
        # Right movement
        elif keys[pygame.K_d] and not keys[pygame.K_a]:
            if self.rect.right < self.end_width:
                self.direction.x = 1
            else:
                self.direction.x = 0
            
        # Apply speed and sprint
        if self.direction.x != 0:
            base_speed = self.speed
            if keys[pygame.K_LSHIFT]:
                base_speed *= self.sprint_multiplier
            self.direction.x *= base_speed

    def _process_jump(self, keys) -> None:
        """Handle jump input"""
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self.direction.y = -self.jump_power
            self.on_ground = False

    def update(self, colliders: list, dt: float) -> None:
        """Update player physics and handle collisions"""
        self._apply_gravity()
        self._update_position()
        self._handle_collisions(colliders)

    def _apply_gravity(self) -> None:
        """Apply gravity to vertical movement"""
        self.direction.y = min(self.direction.y + self.gravity, self.terminal_velocity)

    def _update_position(self) -> None:
        """Update player position based on velocity"""
        self.rect.x += self.direction.x
        self.rect.y += self.direction.y

    def _handle_collisions(self, colliders: list) -> None:
        """Handle collisions with level geometry"""
        for collider in colliders:
            left, right, up, down = collider.check_collision(self.rect)
            
            # Horizontal collisions
            if left:
                self.rect.left = collider.pos[0]
                self.direction.x = 0
            if right:
                self.rect.right = collider.pos[0] + collider.size
                self.direction.x = 0
            
            # Vertical collisions
            if up:
                self.rect.top = collider.pos[1]
                self.direction.y = 0
            if down:
                self.rect.bottom = collider.pos[1] + collider.size
                self.direction.y = 0
                self.on_ground = True

        # Apply gravity if not on ground
        if not self.on_ground:
            self.direction.y += self.gravity

    def draw(self, screen: pygame.Surface, origin: Vector2, start_width: int, end_width: int) -> None:
        """Draw player on screen relative to origin point"""
        self.start_width = start_width
        self.end_width = end_width
        
        draw_rect = self.rect.move(origin.x, origin.y)
        pygame.draw.rect(screen, (255, 0, 0), draw_rect)
