import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import math

import pygame
from pygame.math import Vector2 as vector
from pygame.mouse import get_pos as mouse_pos, get_pressed as mouse_buttons

from src.settings import WINDOW_HEIGHT, WINDOW_WIDTH
from src.save_manager import SaveManager
from src.editor.menu import Menu
from src.editor.settings import (
    TILE_SIZE, MENU_MARGIN, ANIMATION_SPEED, EDITOR_DATA,
    SKY_COLOR, HORIZON_COLOR, HORIZON_TOP_COLOR
)


class Editor:
    def __init__(self):
        # Main setup
        self.display_surface = pygame.display.get_surface()
        self.last_selected_cell = None

        # Fonts
        self._init_fonts()

        # Navigation
        self._init_navigation()

        # Support lines
        self.cols = WINDOW_WIDTH // TILE_SIZE
        self.rows = WINDOW_HEIGHT // TILE_SIZE

        # Menu
        self._init_menu()

        # Selection
        self.selection_index = None
        self.selection_inner_index = None
        self._init_selection()

        # Canvas
        self.layer = 9
        self.canvas_data = {i: {} for i in range(15)}
        self.collider_data = {}
        self.free_move = False

        # Animation
        self.animation_index = 0

        # Save
        self.last_colliders_len = 0
        self.last_tiles_len = 0
        self.last_save_dir = None
        self.filename = 'Новая локация'
        self.save_manager = SaveManager(CanvasObject, None, True)

        # Buttons menu
        self._init_buttons()

    def _init_fonts(self):
        """Initialize fonts for the editor."""
        font_path = r'assets/editor/fonts/press-start-2p-regular.ttf'
        self.main_font = pygame.font.Font(font_path, 12)
        self.tile_font = pygame.font.Font(font_path, 8)

    def _init_navigation(self):
        """Initialize navigation settings."""
        self.origin = vector(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.pan_active = False
        self.pan_offset = vector()

    def _init_menu(self):
        """Initialize menu settings."""
        self.menu = Menu()
        self.page = 1
        self.inner_page = 1
        self.max_page_num = self.menu.get_max_pages()
        self.max_items_on_page = self.menu.max_items_on_page

    def _init_selection(self):
        """Initialize selection settings."""
        self.selection_index = 0
        self.selection_inner_index = 0
        self.start_page = 0
        self.end_page = 0

    def _init_buttons(self):
        """Initialize buttons for the editor."""
        self.button_size = 32
        self.save_button = self._create_button(
            MENU_MARGIN, MENU_MARGIN,
            r'assets/editor/buttons/save_button_0.png',
            r'assets/editor/buttons/save_button_1.png',
            lambda: self.save_scene(False)
        )
        self.save_as_button = self._create_button(
            MENU_MARGIN * 2 + self.button_size, MENU_MARGIN,
            r'assets/editor/buttons/save_as_button_0.png',
            r'assets/editor/buttons/save_as_button_1.png',
            lambda: self.save_scene(True)
        )
        self.new_project_button = self._create_button(
            MENU_MARGIN * 3 + self.button_size * 2, MENU_MARGIN,
            r'assets/editor/buttons/new_file_button_0.png',
            r'assets/editor/buttons/new_file_button_1.png',
            self.create_new_project
        )
        self.open_folder_button = self._create_button(
            MENU_MARGIN * 4 + self.button_size * 3, MENU_MARGIN,
            r'assets/editor/buttons/open_folder_button_0.png',
            r'assets/editor/buttons/open_folder_button_1.png',
            self.import_scene
        )

        self.button_is_over = False
        
        self.buttons = [
            self.save_button,
            self.new_project_button,
            self.save_as_button,
            self.open_folder_button
        ]

    def _create_button(self, x: int, y: int, image1: str, image2: str, action):
        """Helper method to create a button."""
        return Button(x, y, self.button_size, self.button_size, image1, image2, action)

    def start(self) -> None:
        """Set the window caption and icon."""
        pygame.display.set_caption(f'{self.filename} - Редактор')
        editor_icon = pygame.image.load(r'assets/editor/editor_icon.ico')
        pygame.display.set_icon(editor_icon)

    # Support methods
    def get_current_cell(self) -> tuple[int, int]:
        """Calculate current cell based on mouse position and origin.
        
        Returns:
            tuple[int, int]: Column and row coordinates.
        """
        distance_to_origin = vector(mouse_pos()) - self.origin
        return self._calculate_cell_position(distance_to_origin)

    @staticmethod
    def _calculate_cell_position(distance: vector) -> tuple[int, int]:
        """Calculate cell position from distance vector.
        
        Args:
            distance (vector): Distance from origin.
            
        Returns:
            tuple[int, int]: Column and row coordinates.
        """
        col = int(distance.x // TILE_SIZE)
        row = int(distance.y // TILE_SIZE)
        return col, row

    def get_cell_coordinates(self, cell: tuple[int, int]) -> tuple[float, float]:
        """Convert cell position to screen coordinates.
        
        Args:
            cell (tuple[int, int]): Cell column and row.
            
        Returns:
            tuple[float, float]: Screen coordinates.
        """
        col, row = cell
        return (
            col * TILE_SIZE + self.origin.x,
            row * TILE_SIZE + self.origin.y
        )

    def get_free_pos_coordinates(self, pos: tuple[float, float]) -> tuple[float, float]:
        """Convert local coordinates to screen coordinates.
        
        Args:
            pos (tuple[float, float]): Local coordinates.
            
        Returns:
            tuple[float, float]: Screen coordinates.
        """
        x, y = pos
        return x + self.origin.x, y + self.origin.y

    # Validations
    def validate_selection_index(self) -> None:
        """Ensure selection index is within valid range."""
        self.selection_index = max(0, min(
            self.selection_index,
            len(self.menu.indexes) - 1
        ))

        self.selection_index = max(
            self.start_page,
            min(self.selection_index, self.end_page)
        )

    def validate_selection_inner_index(self) -> None:
        """Ensure inner selection index is within valid range."""
        self.selection_inner_index = max(0, min(
            self.selection_inner_index,
            self.menu.max_inner_items - 1
        ))
        self.selection_inner_index = max(
            self.start_page,
            min(self.selection_inner_index, self.end_page)
        )

    def validate_page(self):
        """Ensure page is within valid range."""
        self.page = max(1, min(self.page, self.max_page_num))

    def validate_inner_page(self):
        """Ensure inner page is within valid range."""
        self.inner_page = max(1, min(self.inner_page, math.ceil(self.menu.max_inner_items / self.max_items_on_page)))

    def adjust_selection(self, increment, value=1):
        """Adjust selection index based on increment."""
        if self.menu.inner_mode:
            self.adjust_inner_selection(increment, value)
        else:
            self.adjust_outer_selection(increment, value)

    def adjust_inner_selection(self, increment, value):
        """Adjust inner selection index based on increment."""
        max_items = self.max_items_on_page - 1
        max_inner_items = self.menu.max_inner_items
        inner_page = self.inner_page

        self.end_page = min(max_items, max_inner_items - (self.max_items_on_page * inner_page - max_items + 1))
        
        if self.end_page >= max_items:
            self.end_page -= max_items + 1

        self.end_page = min(self.end_page, max_items - ((self.max_items_on_page * self.inner_page) - max_inner_items))

        self.selection_inner_index += value if increment else -value
        self.validate_selection_inner_index()

    def adjust_outer_selection(self, increment, value):
        """Adjust outer selection index based on increment."""
        self.start_page = 0 if self.page == 1 else self.max_items_on_page * (self.page - 1)
        self.end_page = min(self.start_page + self.max_items_on_page - 1, len(self.menu.indexes) - 1)

        self.selection_index += value if increment else -value
        self.validate_selection_index()

    def validate_layer(self):
        """Ensure layer is within valid range."""
        self.layer = max(0, min(self.layer, 14))

    def event_loop(self):
        """Handle all events in the game loop."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_before_exit()
                if self.on_closing():
                    pygame.quit()
                    sys.exit()

            self.pan_input(event)
            self.buttons_is_over()
            self.menu_click(event)
            self.check_free_move(event)
            self.canvas_add()

            if event.type == pygame.KEYDOWN:
                self.save_scene_hotkeys(event)
                self.page_hotkeys(event)
                self.selection_hotkeys(event)
                self.layer_hotkeys(event)

    def pan_input(self, event):
        """Handle panning input."""
        # Middle mouse button pressed / released
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[1] and not self.menu.rect.collidepoint(
                pygame.mouse.get_pos()):
            self.pan_active = True
            self.pan_offset = vector(pygame.mouse.get_pos()) - self.origin

        if not pygame.mouse.get_pressed()[1]:
            self.pan_active = False

        # Mouse wheel
        if event.type == pygame.MOUSEWHEEL:
            if pygame.key.get_pressed()[pygame.K_LCTRL]:
                self.origin.y -= event.y * 50
            else:
                self.origin.x -= event.y * 50

        # Panning update
        if self.pan_active:
            self.origin = vector(pygame.mouse.get_pos()) - self.pan_offset

    def selection_hotkeys(self, event):
        """Adjust selection based on arrow key input."""
        if event.key == pygame.K_RIGHT:
            self.adjust_selection(True)
        elif event.key == pygame.K_LEFT:
            self.adjust_selection(False)

    def page_hotkeys(self, event):
        """Adjust page based on arrow key input."""
        if event.key == pygame.K_UP:
            if self.menu.inner_mode:
                self.inner_page += 1
                self.validate_inner_page()
            else:
                self.page += 1
                self.validate_page()
            self.adjust_selection(True, self.max_items_on_page)
        elif event.key == pygame.K_DOWN:
            if self.menu.inner_mode:
                self.inner_page -= 1
                self.validate_inner_page()
            else:
                self.page -= 1
                self.validate_page()
            self.adjust_selection(False, self.max_items_on_page)

    def check_free_move(self, event):
        """Check if the free move key is pressed or released."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LCTRL:
                self.free_move = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LCTRL:
                self.free_move = False

    def save_scene_hotkeys(self, event):
        """Save the scene if Ctrl+S is pressed."""
        if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.save_scene(False)

    def layer_hotkeys(self, event):
        """Adjust layer based on key input."""
        if event.key == pygame.K_i:
            self.layer += 1
            self.validate_layer()
        elif event.key == pygame.K_o:
            self.layer -= 1
            self.validate_layer()

    def menu_click(self, event):
        """Handle menu click events."""
        if event.type == pygame.MOUSEBUTTONDOWN and self.menu.rect.collidepoint(pygame.mouse.get_pos()):
            new_selection_index, new_inner_index, inner_page = self.menu.click(
                pygame.mouse.get_pos(),
                pygame.mouse.get_pressed(), self.page,
                self.inner_page
                )
            
            self.selection_index = new_selection_index if new_selection_index is not None else self.selection_index
            self.selection_inner_index = new_inner_index if new_inner_index is not None else self.selection_inner_index
            self.inner_page = inner_page if inner_page is not None else self.inner_page

    # Canvas methods
    def canvas_add(self):
        """
        Handle adding elements to the canvas based on mouse events.

        Args:
            event (pygame.event.Event): The event to handle.
        """
        # Check for left mouse button click outside the menu area
        if mouse_buttons()[0] and not self.menu.rect.collidepoint(mouse_pos()) and not self.button_is_over:
            self.handle_left_click()
            return

        # Check for right mouse button click outside the menu area
        if mouse_buttons()[2] and not self.menu.rect.collidepoint(mouse_pos()) and not self.button_is_over:
            self.handle_right_click()
            return

    def handle_left_click(self):
        """Handle left mouse button click on the canvas."""
        current_cell = self.get_current_cell()
        current_cell_data = self.canvas_data[self.layer].get(current_cell)

        if current_cell_data:
            if self.menu.inner_mode:
                self.handle_inner_mode_selection(current_cell, current_cell_data)
            else:
                self.handle_normal_mode_selection(current_cell, current_cell_data)
        else:
            self.canvas_add_elem(current_cell)

    def handle_right_click(self):
        """Handle right mouse button click on the canvas."""
        current_cell = self.get_current_cell()

        if current_cell in self.canvas_data[self.layer]:
            del self.canvas_data[self.layer][current_cell]

        if self.layer >= 9 and current_cell in self.collider_data:
            del self.collider_data[current_cell]

    def handle_inner_mode_selection(self, current_cell, current_cell_data):
        """
        Handle selection in inner mode.

        Args:
            current_cell (tuple): The current cell coordinates.
            current_cell_data (object): The data of the current cell.
        """
        current_inner_index = current_cell_data.inner_index
        target_inner_index = self.selection_inner_index + ((self.inner_page - 1) * self.max_items_on_page)

        if current_inner_index != target_inner_index:
            self.canvas_add_elem(current_cell)

    def handle_normal_mode_selection(self, current_cell, current_cell_data):
        """
        Handle selection in normal mode.

        Args:
            current_cell (tuple): The current cell coordinates.
            current_cell_data (object): The data of the current cell.
        """
        current_index = current_cell_data.index
        target_index = self.menu.indexes[self.selection_index]

        if current_index != target_index:
            self.canvas_add_elem(current_cell)

    def canvas_add_elem(self, current_cell):
        """
        Add an element to the canvas at the specified cell.

        Args:
            current_cell (tuple): The coordinates of the current cell.
        """
        options = dict(EDITOR_DATA[self.menu.indexes[self.selection_index]])
        is_collider = options['menu'] == 'collider'
        paths = self.menu.get_files_in_directory(options['menu_surf'])

        if self.menu.inner_mode:
            image, path, animation = self._handle_inner_mode(paths, is_collider)
        else:
            image, path, animation = self._handle_normal_mode(paths, is_collider)

        if is_collider:
            if self.can_add_collider(current_cell, path):
                return
            self.add_collider_object(current_cell, image, path, animation)
        else:
            self.add_canvas_object(current_cell, image, path, animation)


    def _handle_inner_mode(self, paths, is_collider):
        image = self.menu.inner_sprite.inner_images_to_draw[self.selection_inner_index]
        path = paths[self.selection_inner_index + ((self.inner_page - 1) * self.max_items_on_page)]

        animation = None
        if not is_collider:
            animation = self._find_animation(self.menu.inner_sprite.animation)

        return image, path, animation

    def _handle_normal_mode(self, paths, is_collider):
        image = None
        animation = None
        path = paths[0]
        for i, sprite in enumerate(self.menu.buttons):
            if i == self.selection_index:
                image = sprite.items[sprite.index][2][0]
                if not is_collider:
                    animation = self._find_animation(sprite.animation)
                break
        return image, path, animation

    def _find_animation(self, animations):
        return next(
            (
                element[self.menu.indexes[self.selection_index]]
                for element in animations
                if self.menu.indexes[self.selection_index] in element
            ),
            None,
        )

    def can_add_collider(self, current_cell, path):
        """
        Check if a collider can be added to the specified cell.

        Args:
            current_cell (tuple): The coordinates of the current cell.
            path (str): The path to the collider image.

        Returns:
            bool: True if the collider can be added, False otherwise.
        """
        if self.layer != 10:
            return False
        
        if current_cell in self.collider_data:
            collider_type = os.path.basename(path).replace('.png', '')
            if self.collider_data[current_cell].collision_type == collider_type:
                return False
                
        return True

    def add_canvas_object(self, current_cell, image, path, animation):
        """
        Add a canvas object to the specified cell.

        Args:
            current_cell (tuple): The coordinates of the current cell.
            image (pygame.Surface): The image of the canvas object.
            path (str): The path to the canvas object image.
            animation (list): The animation frames of the canvas object.
        """
        free_pos = (0, 0)
        if self.free_move:
            x, y = mouse_pos()
            x -= self.origin.x
            y -= self.origin.y
            free_pos = (x, y)

        self.canvas_data[self.layer][current_cell] = CanvasObject(
            self.menu.indexes[self.selection_index],
            self.selection_inner_index + ((self.inner_page - 1) * self.max_items_on_page),
            self.menu.inner_mode,
            current_cell,
            self.layer,
            image,
            path,
            free_pos if self.free_move else None,
            animation
        )

    def add_collider_object(self, current_cell, image, path, animation):
        """
        Add a collider object to the specified cell.

        Args:
            current_cell (tuple): The coordinates of the current cell.
            image (pygame.Surface): The image of the collider object.
            path (str): The path to the collider object image.
            animation (list): The animation frames of the collider object.
        """
        self.collider_data[current_cell] = CanvasObject(
            self.menu.indexes[self.selection_index],
            self.selection_inner_index + ((self.inner_page - 1) * self.max_items_on_page),
            self.menu.inner_mode,
            current_cell,
            9,
            image,
            path,
            None,
            animation
        )

    # Export, import, and create methods
    def save_scene(self, save_as=False):
        """
        Save the current scene.

        Args:
            save_as (bool): If True, prompt for a new save path.
        """
        colliders_len = len(self.collider_data)
        tiles_len = self.get_canvas_data_length()

        if self.last_save_dir is None or save_as:
            self.get_save_path()

        if (self.last_colliders_len != colliders_len or self.last_tiles_len != tiles_len) or save_as:
            self.last_colliders_len = colliders_len
            self.last_tiles_len = tiles_len

            if self.last_save_dir is not None and self.filename is not None:
                self.save_manager.export_scene(self.last_save_dir, self.filename, self.canvas_data, self.collider_data)
            else:
                self.show_error("Ошибка", "Не удалось сохранить сцену. Путь или имя файла не указаны.")

    def import_scene(self):
        """Import a scene from a file."""
        self.save_before_exit()
        if self.on_closing_project():
            self.get_import_path()
            self.reset_parameters()

            if self.last_save_dir is not None and self.filename is not None:
                data = self.save_manager.import_scene(self.last_save_dir, self.filename)

                if data is not None:
                    # Check data structure
                    if data[0]: 
                        self.canvas_data = {i: {} for i in range(15)}  
                        self.collider_data = {} 

                        # Process canvas_data
                        for layer, layer_data in data[0].items():  # Assuming data[0] is canvas_data
                            for coords, canvas_obj in layer_data.items():
                                cell = self._calculate_cell_position(vector(*coords))  # Convert to cell
                                self.canvas_data[layer][cell] = canvas_obj  # Save object in new structure
                                
                    # Process collider_data
                    if data[2]:
                        self.collider_data = data[2]

                else:
                    self.show_error("Ошибка", f"Файлы в дирректории {self.last_save_dir}/{self.filename} не найдены.")
            else:
                self.show_error("Ошибка", "Не удалось импортировать сцену. Путь или имя файла не указаны.")

    @staticmethod
    def get_relative_path(full_path: str) -> str:
        parent_folder = os.path.commonpath([full_path, os.path.abspath(".")])
        relative_path = os.path.relpath(full_path, parent_folder)
        return relative_path

    def get_save_path(self):
        """Prompt the user to select a directory and filename for saving."""
        root = tk.Tk()
        root.withdraw()

        directory = filedialog.askdirectory(title='Выберите директорию для сохранения')
        if not directory:
            self.show_error('Ошибка', 'Директория не выбрана.')
            return

        filename = simpledialog.askstring('Имя файла', 'Введите имя файла для сохранения')
        if not filename:
            self.show_error('Ошибка', 'Имя файла не указано.')
            return

        self.filename = filename
        self.last_save_dir = self.get_relative_path(directory)
        print(self.last_save_dir)

    def get_import_path(self):
        """Prompt the user to select a directory for importing a project."""
        root = tk.Tk()
        root.withdraw()

        directory = filedialog.askdirectory(title='Выберите папку с проектом')
        if not directory:
            self.show_error('Ошибка', 'Папка с проектом не выбрана.')
            return

        self.last_save_dir = os.path.dirname(directory)
        self.filename = os.path.basename(directory)

    @staticmethod
    def show_error(title, message):
        """
        Display an error message.

        Args:
            title (str): The title of the error message.
            message (str): The content of the error message.
        """
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()

    def get_canvas_data_length(self):
        """
        Calculate the total length of canvas data.

        Returns:
            int: The total number of elements in the canvas data.
        """
        return sum(len(layer) for layer in self.canvas_data.values())


    def check_project_updates(self):
        """Check for updates in the project and update the window caption accordingly."""
        colliders_len = len(self.collider_data)
        tiles_len = self.get_canvas_data_length()

        if self.last_colliders_len != colliders_len or self.last_tiles_len != tiles_len:
            pygame.display.set_caption(f'{self.filename}* - Редактор')
            return

        pygame.display.set_caption(f'{self.filename} - Редактор')

    def reset_parameters(self):
        """Reset the editor parameters to their default values."""
        self.last_selected_cell = None
        self.main_font = pygame.font.Font(r'assets/editor/fonts/press-start-2p-regular.ttf', WINDOW_WIDTH // 100)
        self.origin.x = int(WINDOW_WIDTH / 2)
        self.origin.y = int(WINDOW_HEIGHT / 2)
        self.pan_active = False
        self.page = 1
        self.inner_page = 1
        self.max_page_num = self.menu.get_max_pages()
        self.max_items_on_page = self.menu.max_items_on_page
        self.selection_index = 0
        self.selection_inner_index = 0
        self.start_page = 0
        self.end_page = 0
        self.layer = 9
        self.canvas_data = {i: {} for i in range(15)}
        self.collider_data = {}
        self.free_move = False
        self.animation_index = 0
        self.last_colliders_len = None
        self.last_tiles_len = None

    def create_new_project(self):
        """Create a new project, resetting parameters and setting default values."""
        self.save_before_exit()
        if self.on_closing_project():
            self.reset_parameters()
            self.last_save_dir = None
            self.filename = 'Новая локация'

    # Message windows
    def save_before_exit(self):
        """
        Prompt the user to save the project before exiting if there are unsaved changes.

        Returns:
            bool: True if the project was saved or no changes were detected, False otherwise.
        """
        colliders_len = len(self.collider_data)
        tiles_len = self.get_canvas_data_length()

        if self.last_colliders_len != colliders_len or self.last_tiles_len != tiles_len:
            if messagebox.askyesno('Сохранить проект', 'Хотите ли вы сохранить проект?'):
                if self.last_save_dir is not None:
                    self.save_manager.export_scene(self.last_save_dir, self.filename, self.canvas_data, self.collider_data)
                    return True
                self.save_scene(True)
                return True
            return False

    @staticmethod
    def on_closing():
        """
        Prompt the user to confirm exiting the application.

        Returns:
            bool: True if the user confirmed exiting, False otherwise.
        """
        return messagebox.askokcancel('Выход', 'Вы действительно хотите выйти?')

    @staticmethod
    def on_closing_project():
        """
        Prompt the user to confirm closing the current project.

        Returns:
            bool: True if the user confirmed closing the project, False otherwise.
        """
        return messagebox.askokcancel('Новый проект', 'Вы действительно хотите выйти из данного проекта?')

    # Buttons menu methods
    def draw_buttons(self):
        """Draw all buttons on the display surface."""
        for button in self.buttons:
            button.update()
            button.draw(self.display_surface)

    def buttons_is_over(self):
        """Check if any button is being hovered over."""
        for button in self.buttons:
            if button.is_over:
                self.button_is_over = True
                return

        self.button_is_over = False

    # Drawing methods
    def display_sky(self):
        """Display the sky and horizon on the display surface."""

        def draw_horizon_lines():
            """Draw the horizon lines on the display surface."""
            # Define the positions and heights of the horizon lines
            horizon_lines = [
                (self.origin.y - 5, 10),
                (self.origin.y - 12, 4),
                (self.origin.y - 18, 2)
            ]
            # Draw each horizon line
            for y, height in horizon_lines:
                rect = pygame.Rect(0, y, WINDOW_WIDTH, height)
                pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, rect)

        # Fill the background with the sky color
        self.display_surface.fill(SKY_COLOR)

        # If the origin is above the visible window, only draw the sky
        if self.origin.y > WINDOW_HEIGHT + 18:
            return

        # If the origin is within the visible window, draw the ground and horizon lines
        if -18 <= self.origin.y <= WINDOW_HEIGHT + 18:
            # Draw the ground
            ground_rect = pygame.Rect(0, self.origin.y - 5, WINDOW_WIDTH, WINDOW_HEIGHT + 18)
            pygame.draw.rect(self.display_surface, HORIZON_COLOR, ground_rect)

            # Draw the horizon lines
            draw_horizon_lines()
            return

        # If the origin is below the visible window, fill the background with the ground color
        self.display_surface.fill(HORIZON_COLOR)

    def draw_tile_lines(self):
        """Draw the grid lines on the display surface."""
        # Calculate the offset for the origin
        origin_offset = vector(
            x=self.origin.x % TILE_SIZE,
            y=self.origin.y % TILE_SIZE
        )

        # Draw vertical lines
        for i in range(self.cols + 1):
            x = origin_offset.x + i * TILE_SIZE
            if 0 <= x < WINDOW_WIDTH:
                pygame.draw.line(self.display_surface, '#d1aa9d', (x, 0), (x, WINDOW_HEIGHT))

        # Draw horizonal lines
        for i in range(self.rows + 1):
            y = origin_offset.y + i * TILE_SIZE
            if 0 <= y < WINDOW_HEIGHT:
                pygame.draw.line(self.display_surface, '#d1aa9d', (0, y), (WINDOW_WIDTH, y))

    def draw_coords(self):
        """Draw the coordinates relative to the origin on the display surface."""
        x = int(self.origin[0] - (WINDOW_WIDTH // 2))
        y = int(self.origin[1] - (WINDOW_HEIGHT // 2))

        coords = self.main_font.render(f'X: {x} Y: {y}', True, (204, 0, 0))
        self.display_surface.blit(
            coords,
            (WINDOW_WIDTH - (MENU_MARGIN * 2) - coords.get_width(), MENU_MARGIN * 2)
        )

    def draw_layer_num(self):
        """Draw the current layer number on the display surface."""
        layers = self.main_font.render(f'Слой: {self.layer + 1}', True, (180, 0, 0))
        self.display_surface.blit(
            layers,
            (WINDOW_WIDTH - (MENU_MARGIN * 2) - layers.get_size()[0], MENU_MARGIN * 4 + layers.get_height())
        )

    def draw_layers(self, dt):
        """
        Draw all layers on the display surface.

        Args:
            dt (float): The delta time since the last frame.
        """
        self.animation_index += ANIMATION_SPEED * dt
        index = int(self.animation_index)

        for layer in range(1, self.layer + 1):
            self.draw_layer(layer, dt, index)

    def draw_layer(self, layer, dt, index):
        for cell, canvas in self.canvas_data[layer].items():
            pos = self.get_position(canvas, cell)
            if self.is_within_visible_bounds(pos, canvas.size):
                self.draw_canvas_item(canvas, pos, layer, dt, index)

        if layer == 9:
            for cell, collider in self.collider_data.items():
                pos = self.get_cell_coordinates(cell)
                if self.is_within_screen_bounds(pos):
                    self.display_surface.blit(collider.draw_image, pos)

    def get_position(self, canvas, cell):
        if canvas.free_pos:
            return self.get_free_pos_coordinates(canvas.free_pos)  # Use free coordinates
        return self.get_cell_coordinates(cell)  # Use cell coordinates

    def is_within_visible_bounds(self, pos, size):
        return (pos[0] + size[0] > 0 and pos[0] < WINDOW_WIDTH and
                pos[1] + size[1] > 0 and pos[1] < WINDOW_HEIGHT)

    def is_within_screen_bounds(self, pos):
        return (-64 < pos[0] < WINDOW_WIDTH and -64 < pos[1] < WINDOW_HEIGHT)

    def draw_canvas_item(self, canvas, pos, layer, dt, index):
        alpha = max(0, 255 - (self.layer - layer) * 15)
        draw_image = canvas.draw_image.copy()

        if layer != self.layer:
            draw_image.set_alpha(alpha)

        canvas.animation_update(dt, index)
        self.display_surface.blit(draw_image, pos)
        self.draw_canvas_text(canvas, pos)

    def draw_canvas_text(self, canvas, pos):
        if canvas.id is not None:
            color = self.get_canvas_color(canvas)
            if color:
                tile_name = self.tile_font.render(canvas.id, True, color)
                text_rect = tile_name.get_rect(center=(pos[0] + TILE_SIZE // 2, pos[1] - 10))
                self.display_surface.blit(tile_name, text_rect)

    def get_canvas_color(self, canvas):
        if canvas.npc:
            return 'blue'
        if canvas.item:
            return 'green'
        if canvas.event:
            return 'purple'
        return 'red' if canvas.enemy else None
    
    def run(self, dt):
        """
        Run the main loop of the editor.

        Args:
            dt (float): The delta time since the last frame.
        """
        self.event_loop()

        # Drawing
        self.display_sky()  # Draw sky (layer 0)
        self.draw_layers(dt)  # Draw all layers

        self.draw_tile_lines()  # Draw tile lines
        pygame.draw.circle(self.display_surface, 'red', self.origin, 5)  # Draw origin point

        # Display menu
        self.menu.display(
            self.menu.indexes[self.selection_index],
            self.selection_inner_index,
            self.page, self.inner_page
        )

        self.draw_coords()  # Draw coordinates
        self.draw_layer_num()  # Draw layer number
        self.draw_buttons()  # Draw buttons

        self.check_project_updates()  # Check for project updates


class CanvasObject:
    def __init__(self, index, inner_index, inner_mode=False, tile=(0, 0), layer=10, image=None, image_path='', free_pos=None, animation=None):
        self.objects = []
        self.index = index
        self.inner_index = inner_index
        self.inner_mode = inner_mode
        self.tile = tile
        self.free_pos = free_pos
        self.free_pos_to_save = free_pos

        # Object type flags
        self.item = False
        self.npc = False
        self.enemy = False
        self.player = False
        self.event = False
        self.id = None

        self.layer = layer  # Layer range: 3 - 14
        self.collision_type = ''

        # Animation attributes
        self.animation = animation
        self.animation_dir = ''

        # Image attributes
        self.path_to_image = image_path
        self.image = image
        self.size = self.image.get_size() if image else (0, 0)
        self.draw_image = self.image.copy() if image else None

        self.add_object_by_index()

    def get_npc_id(self):
        """
        Prompt the user to determine if the NPC is canonical and get its ID.

        Returns:
            str: The ID of the NPC if canonical, None otherwise.
        """
        root = tk.Tk()
        root.withdraw()

        response = messagebox.askyesno('Каноничный персонаж', 'Это каноничный персонаж?')
        root.destroy()

        if response:
            return self.get_id_name('Имя NPC', 'Введите имя для NPC:')
        return None

    @staticmethod
    def get_id_name(title='', prompt=''):
        """
        Prompt the user to enter an ID name.

        Args:
            title (str): The title of the prompt window.
            prompt (str): The prompt message.

        Returns:
            str: The entered ID name.
        """
        root = tk.Tk()
        root.withdraw()

        answer = simpledialog.askstring(title, prompt)
        root.destroy()

        return answer

    def add_object_by_index(self) -> None:
        """Add an object to the canvas based on its index."""
        if self.index is None:
            return

        options = EDITOR_DATA[self.index]

        # Set animation directory if available
        self.animation_dir = options.get('graphics')

        # Determine object type and set layer if required
        layer_required = False
        match options['style']:
            case 'player':
                self.player = True
                layer_required = True
            case 'item':
                self.item = True
                layer_required = True
                self.id = self.get_id_name('Название предмета', 'Введите название предмета:')
            case 'enemy':
                self.enemy = True
                layer_required = True
                self.id = self.get_id_name('Название врага', 'Введите название врага:')
            case 'event':
                self.event = True
                layer_required = True
                self.id = self.get_id_name('Название события', 'Введите название события:')
            case 'npc':
                self.npc = True
                layer_required = True
                self.id = self.get_npc_id()

        if options['menu'] == 'collider':
            self.collision = True
            self.collision_type = os.path.basename(self.path_to_image).replace('.png', '')
            layer_required = True

        if layer_required:
            self.layer = 10

    def animation_update(self, dt, index):
        """
        Update the animation frame of the object.

        Args:
            dt (float): The delta time since the last frame.
            index (int): The current animation frame index.
        """
        if self.animation:
            index %= len(self.animation)
            self.draw_image = self.animation[index]


class Button:
    def __init__(self, x, y, width, height, image1, image2, action=None):
        self.rect = pygame.Rect(x, y, width, height)

        self.image1 = pygame.image.load(image1).convert()
        self.image2 = pygame.image.load(image2).convert()
        self.image1 = pygame.transform.scale(self.image1, (width, height))
        self.image2 = pygame.transform.scale(self.image2, (width, height))

        self.image = self.image1
        self.is_over = False
        self.action = action
        self.clicked = False

    def draw(self, screen):
        """
        Draw the button on the screen.

        Args:
            screen (pygame.Surface): The surface to draw the button on.
        """
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        """Update the button state based on mouse interaction."""
        mouse_pos_current = mouse_pos()

        if self.rect.collidepoint(mouse_pos_current):
            self.image = self.image2
            self.is_over = True
            if mouse_buttons()[0] and not self.clicked:
                self.clicked = True
                if self.action:
                    self.action()
        else:
            self.image = self.image1
            self.is_over = False

        if not mouse_buttons()[0]:
            self.clicked = False
