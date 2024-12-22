import pygame
import sys
import os
from pygame.math import Vector2
from src.settings import PLAYER_PATH, PLAYER_ANIMATION_SPEED, PLAYER_WIDTH, PLAYER_HEIGHT


class Player:
    """Represents the player character in the game"""

    def __init__(self):
        """Initialize player with dimensions and physics properties"""
        # Physical properties
        self.rect = pygame.Rect(0, 0, PLAYER_WIDTH, PLAYER_HEIGHT)
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

        # Animation parameters
        self.animation_names = ['idle', 'run', 'jump', 'slide', 'attack', 'jump_attack']  # Animation names
        self.animation_key = self.animation_names[0]
        self.animation_frames = self.load_animation_frames()  # Load animation frames
        if self.animation_frames:  # Check if frames are loaded
            self.current_frame = 0  # Current animation frame
            self.frame = 0.0
            self.image = self.animation_frames['idle_right'][self.current_frame]  # Initial image
        else:
            print("Warning: No animation frames loaded. Using a default image.")
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))  # Create a blank surface as a fallback image

        self.animation_speed = PLAYER_ANIMATION_SPEED  # Set animation speed
        self.last_direction = 'idle'  # Store last direction
        self.is_jumping = False  # Track if the player is jumping
        self.is_sliding = False  # Track if the player is sliding
        self.current_slide_speed = 0  # Current speed during sliding
        self.slide_duration = 0.5  # Duration of the slide in seconds
        self.slide_timer = 0  # Timer for the slide duration
        self.slide_deceleration = 0.1  # Deceleration factor for sliding
        self.is_sprinting = False  # Track if the player is sprinting
        self.is_attacking = False  # Track if the player is attacking
        self.attack_timer = 0  # Timer for the attack duration
        self.attack_damage = 10  # Example damage value

    def load_animation_frames(self):
        """Load animation frames for the player"""
        frames = {}

        for animation in self.animation_names:
            frames[f'{animation}_right'] = []
            frames[f'{animation}_left'] = []

            # Path to the animation folder
            animation_path = os.path.join(PLAYER_PATH, animation)

            # Check if the animation folder exists
            if not os.path.exists(animation_path):
                continue

            # Load frames for right animation
            for image_file in os.listdir(animation_path):  # Look for all files in the folder
                if image_file.endswith('.png'):  # Check if the file is a PNG
                    image_path = os.path.join(animation_path, image_file)
                    image = pygame.image.load(image_path).convert_alpha()
                    image = pygame.transform.scale(image, (PLAYER_WIDTH, PLAYER_HEIGHT))  # Scale the image
                    frames[f'{animation}_right'].append(image)

            # Load frames for left animation (flip)
            for image in frames[f'{animation}_right']:
                frames[f'{animation}_left'].append(pygame.transform.flip(image, True, False))

        return frames

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

        # Check for jumping
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self._process_jump(keys)  # Handle jump input

        # Check for sliding
        if not self.is_sliding:
            self._process_slide(keys)
            
        self._process_attack(keys)

        # Horizontal movement
        if not self.is_sliding:  # Prevent horizontal movement if sliding
            self._process_horizontal_movement(keys)
        elif (not keys[pygame.K_s] and self.current_slide_speed > 0 and 
            ((keys[pygame.K_a] and self.last_direction == 'run_right') or 
            (keys[pygame.K_d] and self.last_direction == 'run_left'))):
            self.is_sliding = False  # Stop sliding if opposite direction is pressed

    def _process_horizontal_movement(self, keys) -> None:
        """Handle horizontal movement based on keyboard input"""
        if self.is_sliding:
            return  # Prevent horizontal movement if sliding

        # Reset horizontal velocity
        self.direction.x = 0

        # Left movement
        if keys[pygame.K_a] and not keys[pygame.K_d]:
            if self.rect.left > self.start_width:
                self.direction.x = -1
                self.last_direction = 'run_left'  # Update last direction
        # Right movement
        elif keys[pygame.K_d] and not keys[pygame.K_a]:
            if self.rect.right < self.end_width:
                self.direction.x = 1
                self.last_direction = 'run_right'  # Update last direction

        # Check for sprinting
        if keys[pygame.K_LSHIFT]:
            self.is_sprinting = True  # Set sprinting state
        else:
            self.is_sprinting = False  # Reset sprinting state

        # Apply speed and sprint
        if self.direction.x != 0:
            base_speed = self.speed
            if self.is_sprinting:
                base_speed *= self.sprint_multiplier
            self.direction.x *= base_speed

    def _process_jump(self, keys) -> None:
        """Handle jump input"""
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self.direction.y = -self.jump_power
            self.on_ground = False
            self.is_jumping = True  # Set jumping state
            self.is_sliding = False  # Stop sliding when jumping
            self.animation_key = 'jump_right' if self.last_direction == 'run_right' else 'jump_left'  # Set jump animation

    def _process_slide(self, keys) -> None:
        """Handle sliding input"""
        if self.on_ground and not self.is_sliding and (keys[pygame.K_s] and (keys[pygame.K_a] or keys[pygame.K_d])):
            self.is_sliding = True  # Start sliding
            self.slide_timer = self.slide_duration  # Reset slide timer
            self.animation_key = 'slide_right' if self.last_direction == 'run_right' else 'slide_left'  # Set slide animation
            self.current_frame = 0  # Reset to the first frame of the slide animation

            # Calculate the initial slide speed based on current direction
            if keys[pygame.K_a] or keys[pygame.K_d]:  # If moving left
                self.current_slide_speed = self.current_slide_speed * 1.5  # Adjust the multiplier as needed

    def _process_attack(self, keys) -> None:
        """Handle attack input"""
        if keys[pygame.K_f] and not self.is_attacking:  # Ground attack key
            self.current_frame = 0  # Reset to the first frame of the air attack animation
            self.is_attacking = True  # Set attacking state
            self.attack_timer = 0.25  # Duration of the attack (can be adjusted)
            
            if not self.on_ground:  # Air attack key
                self.animation_key = 'jump_attack_right' if self.last_direction == 'run_right' else 'jump_attack_left'  # Set air attack animation
                return
            
            self.animation_key = 'attack_right' if self.last_direction == 'run_right' else 'attack_left'  # Set attack animation

    def update(self, colliders: list, dt: float) -> None:
        """Update player physics and handle collisions"""
        if self.is_attacking:
            self.attack_timer -= dt  # Decrease the attack timer
            if self.attack_timer <= 0:
                self.is_attacking = False  # End attacking
                self.animation_key = 'idle_right' if self.last_direction == 'run_right' else 'idle_left'  # Return to idle animation

        if self.is_sliding:
            self.slide_timer -= dt  # Decrease the slide timer
            if self.slide_timer <= 0 or abs(self.current_slide_speed) < 0.1:
                self.is_sliding = False  # End sliding
                self.current_slide_speed = 0  # Reset slide speed
            else:
                # Apply deceleration to current slide speed
                self.current_slide_speed -= self.slide_deceleration * dt
                if abs(self.current_slide_speed) < 0.1:  # Stop sliding if speed is very low
                    self.is_sliding = False
                    self.current_slide_speed = 0
        else:
            self.current_slide_speed = self.speed

        self._apply_gravity()
        self._update_position()
        self._handle_collisions(colliders)
        self._update_animation(dt)

    def _apply_gravity(self) -> None:
        """Apply gravity to vertical movement"""
        self.direction.y = min(self.direction.y + self.gravity, self.terminal_velocity)

    def _update_position(self) -> None:
        """Update player position based on velocity"""
        if self.is_sliding:
            # Calculate new position based on current sliding speed
            new_x = self.rect.x + self.current_slide_speed * (1 if self.last_direction == 'run_right' else -1)

            # Check boundaries
            if new_x < self.start_width:
                new_x = self.start_width  # Prevent going beyond the left boundary
                self.is_sliding = False  # Stop sliding if hitting the boundary
            elif new_x + self.rect.width > self.end_width:
                new_x = self.end_width - self.rect.width  # Prevent going beyond the right boundary
                self.is_sliding = False  # Stop sliding if hitting the boundary

            self.rect.x = new_x  # Update the player's position
        else:
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
                if self.is_sliding:
                    self.is_sliding = False  # Stop sliding on collision
            if right:
                self.rect.right = collider.pos[0] + collider.size
                self.direction.x = 0
                if self.is_sliding:
                    self.is_sliding = False  # Stop sliding on collision
            
            # Vertical collisions
            if up:
                self.rect.top = collider.pos[1]
                self.direction.y = 0
            if down:
                self.rect.bottom = collider.pos[1] + collider.size
                self.direction.y = 0
                self.on_ground = True  # Set on_ground to True when landing
                self.is_jumping = False  # Reset jumping state when landing

        # Apply gravity if not on ground
        if not self.on_ground:
            self.direction.y += self.gravity

    def _update_animation(self, dt: float) -> None:
        """Update the current frame of the animation"""
        if self.is_sliding or self.is_attacking:  # If the player is sliding
            # Update the current frame of the slide animation
            self.frame += self.animation_speed * dt
            self.current_frame = int(self.frame)

            if self.current_frame >= len(self.animation_frames[self.animation_key]):
                self.current_frame = len(self.animation_frames[self.animation_key]) - 1  # Hold on the last frame
        elif self.is_jumping:  # If the player is jumping
            self.animation_key = 'jump_right' if self.last_direction == 'run_right' else 'jump_left'
            self.current_frame = 0  # Reset to the first frame of the jump animation
        elif self.on_ground and self.direction.x != 0:  # If the player is moving on the ground
            self.animation_key = 'run_right' if self.direction.x > 0 else 'run_left'
            self.current_frame = 0  # Reset to the first frame of the run animation
        elif self.on_ground and self.direction.x == 0:  # If the player is idle
            self.animation_key = 'idle_right' if self.last_direction == 'run_right' else 'idle_left'
            self.current_frame = 0  # Reset to the first frame of the idle animation

        # Update the current frame of the animation
        self.frame += self.animation_speed * dt
        self.current_frame = int(self.frame)

        if self.current_frame >= len(self.animation_frames[self.animation_key]):
            if self.animation_key in ['jump_left', 'jump_right']:
                self.current_frame = len(self.animation_frames[self.animation_key]) - 1  # Hold on the last frame
            else:
                self.current_frame = 0  # Reset to the first frame for other animations
                self.frame = 0

        # Update the image based on direction
        self.image = self.animation_frames[self.animation_key][self.current_frame % len(self.animation_frames[self.animation_key])]
        
    def draw(self, screen: pygame.Surface, origin: Vector2, start_width: int, end_width: int) -> None:
        """Draw player on screen relative to origin point"""
        self.start_width = start_width
        self.end_width = end_width
        
        draw_rect = self.rect.move(origin.x, origin.y)
        screen.blit(self.image, draw_rect)  # Draw the current player image
