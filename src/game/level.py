import pygame
import random
import math

from pygame.math import Vector2

from settings import *
from save_manager import SaveManager


class Level:
    """Represents the game level"""
    
    def __init__(self, path, switch, player):
        """Initialize level with path, switch, and player"""
        # Main setup
        self.display_surface = pygame.display.get_surface()
        self.switch = switch
        self.player = player
        self.path = path

        # Camera origin point
        self.origin = Vector2(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        # Layer management
        self.canvas_data = {i: {} for i in range(15)}
        self.collider_data = {}

        # Animation state
        self.animation_index = 0
        self.tile_size = None
        self.animation_speed = None
        self.camera_speed_on_layer = None

        # Visual settings
        self.sky_color = None
        self.horizon_color = None
        self.horizon_top_color = None

        # Scene initialization
        self.save_manager = SaveManager(TileObject, Collider, False)
        self.import_scene()
        self.set_player_coords()
        self.player.set_coords(self.origin)
        
        # Level dimensions
        self.start_width, self.end_width = self.get_scene_width()

        # Camera target
        self.target = pygame.Vector2(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        # Parallax layers setup
        self._setup_parallax_layers()

    def _setup_parallax_layers(self):
        """Initialize sky and cloud parallax layers"""
        # Sky layer (layer 1)
        self.sky_vector = self.origin.copy()
        self.sky_delay = 0.25

        # Clouds layer (layer 2)
        self.clouds_vector = self.origin.copy()
        self.clouds_delay = 0.1
        self.clouds = {}
        self.initialize_clouds()
        
        # Background layers (layer 3), (layer 4)
        self.background_layers = {}
        
        # Foreground layers (layer 13), (layer 14)
        self.foreground_layers = {}
        
        self._setup_background_layers()
        self._setup_foreground_layers()

    # Sky (layer 1)
    def display_sky(self):
        """Render sky background with parallax effect"""
        # Smooth sky following camera
        self.sky_vector.y += (self.target.y - self.sky_vector.y) * (1 - math.cos(math.pi * self.sky_delay))
        y = self.origin.y - self.sky_vector.y - 35

        # Background layers
        self.display_surface.fill(self.sky_color)
        
        # Ground and horizon rendering
        self._render_horizon_layers(y)

    def _render_horizon_layers(self, y):
        """Render ground and horizon line layers"""
        # Main ground layer
        ground_rect = pygame.Rect(0, -y - 5, WINDOW_WIDTH, WINDOW_HEIGHT + 18)
        pygame.draw.rect(self.display_surface, self.horizon_color, ground_rect)

        # Multiple horizon lines for depth effect
        horizon_lines = [
            (-y - 5, 10),
            (-y - 12, 4),
            (-y - 18, 2)
        ]
        for line_y, height in horizon_lines:
            rect = pygame.Rect(0, line_y, WINDOW_WIDTH, height)
            pygame.draw.rect(self.display_surface, self.horizon_top_color, rect)

    # Clouds (layer 2)
    def initialize_clouds(self):
        """Initialize cloud objects with randomized properties"""
        for cell, canvas in self.canvas_data[1].items():
            self.clouds[cell] = {
                'canvas': canvas,
                'speed': random.uniform(0.2, 0.5),  # Base movement speed
                'offset': random.uniform(self.start_width, self.end_width),  # Initial horizontal offset
                'y_offset': random.uniform(-200, 150)  # Vertical variation
            }
    
    def display_clouds(self, index):
        """Update and render cloud layer with parallax effect"""
        # Update cloud layer position
        self._update_cloud_layer()

        # Process each cloud
        for data in self.clouds.values():
            self._process_cloud(data, index)

    def _update_cloud_layer(self):
        """Update the overall cloud layer position"""
        self.clouds_vector.y += (self.target.y - self.clouds_vector.y) * self.clouds_delay

    def _process_cloud(self, data, index):
        """Process individual cloud movement and rendering"""
        canvas = data['canvas']
        pos = list(canvas.pos)
        cloud_width = canvas.size[0]
        cloud_height = canvas.size[1]

        # Ensure cloud data initialization
        self._ensure_cloud_data(data)

        # Update cloud position
        screen_pos = self._update_cloud_position(pos, data)

        # Handle cloud recycling
        self._handle_cloud_recycling(screen_pos, data, cloud_width)

        # Render cloud if visible
        if self._is_cloud_visible(screen_pos, cloud_width, cloud_height):
            canvas.animation_update(index)
            self.display_surface.blit(canvas.draw_image, screen_pos)

    def _ensure_cloud_data(self, data):
        """Ensure all necessary cloud data exists"""
        if 'offset' not in data:
            data['offset'] = 0
        if 'y_offset' not in data:
            data['y_offset'] = random.uniform(-200, 150)

    def _update_cloud_position(self, pos, data):
        """Calculate cloud position with smooth movement"""
        data['offset'] += data['speed'] * 60 * 0.01
        screen_pos = list(self.get_free_pos_coordinates(pos))
        
        # Update positions with parallax effect
        screen_pos[0] = pos[0] + data['offset']
        screen_pos[1] = 100 + data['y_offset'] + (self.target.y * 0.05)
        
        return screen_pos

    def _handle_cloud_recycling(self, screen_pos, data, cloud_width):
        """Handle cloud recycling when moving off location"""
        if screen_pos[0] > (self.end_width // 2) + WINDOW_WIDTH + cloud_width:
            data['offset'] = self.start_width - WINDOW_WIDTH - cloud_width
            data['y_offset'] = random.uniform(-200, 150)

    def _is_cloud_visible(self, pos, width, height):
        """Check if cloud is within visible screen bounds"""
        return (pos[0] + width > -width and 
                pos[0] < WINDOW_WIDTH + width and
                pos[1] + height > -height and 
                pos[1] < WINDOW_HEIGHT + height)
        
    # Background layers (layer 3), (layer 4)
    def _setup_background_layers(self):
        """Initialize background layers for parallax effect"""
        self.background_layers = {
            2: {
                'vector': self.origin.copy(),
                'delay': 0.5,  # Delay for the first background layer
                'tiles': []  # This will hold the tiles for this layer
            },
            3: {
                'vector': self.origin.copy(),
                'delay': 0.3,  # Delay for the second background layer
                'tiles': []  # This will hold the tiles for this layer
            }
        }
        self.initialize_background_tiles()

    def initialize_background_tiles(self):
        """Initialize background tiles for layers"""
        # Use existing tiles from canvas_data
        for layer in range(2, 4):
            for canvas in self.canvas_data[layer].values():
                self.background_layers[layer]['tiles'].append(canvas)

    def display_background_layers(self, index):
        """Render background layers with parallax effect"""
        for layer_data in self.background_layers.values():
            self._update_background_layer(layer_data)
            self._render_background_layer(layer_data, index),

    def _update_background_layer(self, layer_data):
        """Update the background layer position for parallax effect"""
        layer_data['vector'].x = self.origin.x * layer_data['delay']
        layer_data['vector'].y = self.origin.y - (self.origin.y * layer_data['delay']) + 200

    def _render_background_layer(self, layer_data, index):
        """Render a specific background layer"""
        # Render tiles and check for off-screen repositioning
        for tile in layer_data['tiles']:
            # Calculate the position for the tile
            y_offset = layer_data['vector'].y + tile.pos[1]
            tile_pos = tile.pos[0] + layer_data['vector'].x * layer_data['delay']

            # Update animation if available
            if tile.animation is not None:
                tile.animation_update(index)  # Assuming you have an update method for animation

            # Render the tile
            self.display_surface.blit(tile.draw_image, (tile_pos, y_offset))

            # Handle infinite background scrolling
            if tile_pos < -tile.size[0]:
                # Move the tile to the right by creating a new position
                new_pos = (tile.pos[0] + self.end_width * len(layer_data['tiles']), tile.pos[1])
                tile.pos = new_pos  # Update the tile's position
            elif tile_pos > WINDOW_WIDTH:
                # Move the tile to the left by creating a new position
                new_pos = (tile.pos[0] - self.end_width * len(layer_data['tiles']), tile.pos[1])
                tile.pos = new_pos  # Update the tile's position
                
            old_pos = tile_pos

            # Check for gaps on the right
            while tile_pos < WINDOW_WIDTH:
                new_tile_pos = tile_pos + tile.size[0]
                self.display_surface.blit(tile.draw_image, (new_tile_pos, y_offset))
                tile_pos = new_tile_pos

            # Check for gaps on the left
            while old_pos >= 0:
                new_tile_pos = old_pos - tile.size[0]
                self.display_surface.blit(tile.draw_image, (new_tile_pos, y_offset))
                old_pos = new_tile_pos
                
    def _setup_foreground_layers(self):
        """Initialize foreground layers for parallax effect"""
        self.foreground_layers = {
            13: {
                'vector': self.origin.copy(),
                'delay': 0.8,  # Delay for the first foreground layer
                'tiles': []  # This will hold the tiles for this layer
            },
            14: {
                'vector': self.origin.copy(),
                'delay': 0.85,  # Delay for the second foreground layer
                'tiles': []  # This will hold the tiles for this layer
            }
        }
        self.initialize_foreground_tiles()

    def initialize_foreground_tiles(self):
        """Initialize foreground layer tiles"""
        # Use existing tiles from canvas_data
        for layer in range(13, 15):
            for canvas in self.canvas_data[layer].values():
                self.foreground_layers[layer]['tiles'].append(canvas)
                
    def _update_foreground_layer(self, layer_data):
        """Update the foreground layer position for parallax effect"""
        layer_data['vector'].x = self.origin.x * layer_data['delay']
        layer_data['vector'].y = self.origin.y - (self.origin.y * (layer_data['delay'] * 0.7)) + 60


    def display_foreground_layers(self, index):
        """Render foreground layers with parallax effect"""
        for layer_data in self.foreground_layers.values():
            self._update_foreground_layer(layer_data)  # Update position based on delay
            self._render_foreground_layer(layer_data, index)

    def _render_foreground_layer(self, layer_data, index):
        """Render a specific foreground layer"""
        # Render tiles
        for tile in layer_data['tiles']:
            # Calculate the position for the tile
            y_offset = layer_data['vector'].y + tile.pos[1]
            tile_pos = tile.pos[0] + layer_data['vector'].x

            # Update animation if available
            if tile.animation is not None:
                tile.animation_update(index)  # Update animation frame
                
            # Check for off-screen positioning
            if tile_pos < -tile.size[0] or tile_pos > WINDOW_WIDTH:
                continue  # Do not render tile if it is off-screen
            
            # Render the tile
            self.display_surface.blit(tile.draw_image, (tile_pos, y_offset))

        # Handle infinite scrolling for foreground layers
        for tile in layer_data['tiles']:
            tile_pos = tile.pos[0] + layer_data['vector'].x
            if tile_pos < -tile.size[0]:
                # Move tile to the right
                tile.pos = (tile.pos[0] + self.end_width * len(layer_data['tiles']), tile.pos[1])
            elif tile_pos > WINDOW_WIDTH:
                # Move tile to the left
                tile.pos = (tile.pos[0] - self.end_width * len(layer_data['tiles']), tile.pos[1])

    # import
    def import_scene(self):
        """Import scene settings and data from save file"""
        # Load scene data
        data = self.save_manager.import_scene(self.path, '')
        self.canvas_data = data[0]
        settings_data = data[1]
        self.collider_data = data[2]

        # Apply visual and gameplay settings
        self._apply_scene_settings(settings_data)

    def _apply_scene_settings(self, settings):
        """Apply imported scene settings"""
        self.tile_size = settings['tile_size']
        self.animation_speed = settings['animation_speed']
        self.camera_speed_on_layer = settings['camera_speed_on_layer']
        self.sky_color = settings['sky_color']
        self.horizon_color = settings['horizon_color']
        self.horizon_top_color = settings['horizon_top_color']

    def set_player_coords(self):
        """Find and set initial player coordinates"""
        for cell, canvas in self.canvas_data[9].items():
            if canvas.player:
                self._set_origin_from_canvas(canvas)
                del self.canvas_data[9][cell]
                break
            
    def get_scene_width(self):
        """Get the width of the scene"""
        start_width = 0
        end_width = 0
        
        for layer in range(3, 13):
            for canvas in self.canvas_data[layer].values():
                pos = self.get_free_pos_coordinates(canvas.pos)
                if pos[0] < start_width:
                    start_width = pos[0]
                if pos[0] + canvas.size[0] > end_width:
                    end_width = pos[0] + canvas.size[0]
                    
        start_width -= self.origin.x
        end_width -= self.origin.x
        return start_width, end_width

    def _set_origin_from_canvas(self, canvas):
        """Set origin point from canvas position"""
        self.origin.x = canvas.pos[0]
        self.origin.y = canvas.pos[1]

    def update_target(self, camera):
        """Update camera target position"""
        self.target.y = camera.centery

    def get_free_pos_coordinates(self, pos):
        """Convert local coordinates to screen coordinates"""
        return (pos[0] + self.origin.x, pos[1] + self.origin.y)

    def draw_layers(self, index):
        """Draw all game layers with proper ordering"""
        # Update animation state

        # Draw each layer
        for layer in range(4, 13):
            self._draw_layer_contents(layer, index)
            
            # Draw player on specific layer
            if layer == 10:
                self.player.draw(self.display_surface, self.origin, self.start_width, self.end_width)

    def _draw_layer_contents(self, layer, index):
        """Draw all objects in the specified layer"""
        for canvas in self.canvas_data[layer].values():
            pos = self.get_free_pos_coordinates(canvas.pos)
            
            # Check visibility before drawing
            if self._is_object_visible(pos, canvas.size):
                canvas.animation_update(index)
                self.display_surface.blit(canvas.draw_image, pos)

    def _is_object_visible(self, pos, size):
        """Check if object is within screen bounds"""
        return (pos[0] + size[0] > 0 and 
                pos[0] < WINDOW_WIDTH and
                pos[1] + size[1] > 0 and 
                pos[1] < WINDOW_HEIGHT)

    def draw(self, dt, coords=(0, 0)):
        """Main draw method for the level"""
        # Update camera position
        self.origin.x = coords[0]
        self.origin.y = coords[1]
        
        # Draw all elements in proper order
        self.animation_index += self.animation_speed * dt
        index = int(self.animation_index)
        # Draw background layers
        self.display_sky()
        self.display_clouds(index)
        self.display_background_layers(index)
        
        # Draw layers
        self.draw_layers(index)
        
        # Draw foreground
        self.display_foreground_layers(index)


class Collider:
    """Handles collision detection and boundaries"""
    
    def __init__(self, layer=10, pos=None, collider_type=None, size=64):
        """Initialize collider with position and type"""
        self.pos = pos
        self.layer = layer  # Layer range: 3 - 14
        self.collider_type = collider_type
        self.size = size
        self.rects = self._create_collision_rects()

    def _create_collision_rects(self):
        """Create collision rectangles based on collider type"""
        rects = {}
        
        # Create specific collision rectangles based on type
        if 'l' in self.collider_type:
            rects['left'] = self._create_left_rect()
        if 'r' in self.collider_type:
            rects['right'] = self._create_right_rect()
        if 'u' in self.collider_type:
            rects['up'] = self._create_up_rect()
        if 'd' in self.collider_type:
            rects['down'] = self._create_down_rect()
            
        return rects

    def _create_left_rect(self):
        """Create left collision rectangle"""
        return pygame.Rect(self.pos[0], self.pos[1], 1, self.size)

    def _create_right_rect(self):
        """Create right collision rectangle"""
        return pygame.Rect(self.pos[0] + self.size - 1, self.pos[1], 1, self.size)

    def _create_up_rect(self):
        """Create upper collision rectangle"""
        return pygame.Rect(self.pos[0], self.pos[1], self.size, 1)

    def _create_down_rect(self):
        """Create lower collision rectangle"""
        return pygame.Rect(self.pos[0], self.pos[1] + self.size - 1, self.size, 1)

    def check_collision(self, rect):
        """Check collision with provided rectangle"""
        return (
            ('left' in self.rects and self.rects['left'].colliderect(rect)),
            ('right' in self.rects and self.rects['right'].colliderect(rect)),
            ('up' in self.rects and self.rects['up'].colliderect(rect)),
            ('down' in self.rects and self.rects['down'].colliderect(rect))
        )


class TileObject:
    """Represents a tile object in the game world"""
    
    def __init__(self, layer=10, image=None, pos=None, animation=None):
        """Initialize tile object with position and visual properties"""
        self.pos = pos
        self.layer = layer  # Layer range: 3 - 14

        # Object type flags
        self._initialize_flags()

        # Visual properties
        self.animation = animation
        self.image = image
        self.size = None
        self.draw_image = self.image.copy() if image else None

    def _initialize_flags(self):
        """Initialize object type flags"""
        self.item = False
        self.npc = False
        self.enemy = False
        self.player = False
        self.event = False
        self.id = None

    def animation_update(self, index):
        """Update object animation if available"""
        if self.animation:
            index %= len(self.animation)
            self.draw_image = self.animation[index]
