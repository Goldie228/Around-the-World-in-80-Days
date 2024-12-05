"""Menu system for the editor interface"""
from typing import Dict, List, Optional, Tuple, Union
import os
import math
from pathlib import Path

import pygame
from pygame.sprite import Group, Sprite
from pygame.surface import Surface
from pygame.rect import Rect
from pygame.image import load

from settings import WINDOW_WIDTH, WINDOW_HEIGHT
from editor.settings import (
    TILE_SIZE, MENU_MARGIN, EDITOR_DATA,
    BUTTON_BG_COLOR, BUTTON_LINE_COLOR, MENU_LINE_COLOR
)


class Menu:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.create_data()
        self.create_buttons()

        # Create a surface for buttons with adjusted size
        self.buttons_surf = pygame.Surface(
            (self.rect.size[0] - (self.margin * 2), self.rect.size[1] - (self.margin * 2))
        )

        self.inner_mode = False
        self.inner_sprite = None
        self.max_inner_items = 0

        self.old_page = None
        self.start_page = None

    @staticmethod
    def get_files_in_directory(directory_path):
        """
        Get a list of files in the specified directory.

        Args:
            directory_path (str): The path to the directory.

        Returns:
            list: A list of file paths.
        """
        parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        directory_path = os.path.join(parent_path, directory_path)
        items = os.listdir(directory_path)
        files = [os.path.join(directory_path, item) for item in items if os.path.isfile(os.path.join(directory_path, item))]
        return files

    def create_data(self):
        """Create the data for the menu surfaces."""
        self.menu_surfs = {}
        self.indexes = []

        for i, (key, value) in enumerate(EDITOR_DATA.items()):
            if value['menu'] and value['menu_surf']:
                paths = self.get_files_in_directory(value['menu_surf'])
                inner_items = [load(path).convert_alpha() for path in paths]
                first_image = load(paths[0]).convert_alpha()

                if value['menu'] not in self.menu_surfs:
                    self.menu_surfs[value['menu']] = [(key, first_image, inner_items)]
                    self.indexes.append(i)
                else:
                    self.menu_surfs[value['menu']].append((key, first_image, inner_items))

    def get_max_pages(self):
        """
        Get the maximum number of pages for the menu.

        Returns:
            int: The maximum number of pages.
        """
        return math.ceil(len(self.menu_surfs) / self.max_items_on_page)

    def create_rects(self, len_value):
        """
        Create rectangles for the buttons.

        Args:
            len_value (int): The number of buttons.

        Returns:
            list: A list of button rectangles.
        """
        buttons_list = []
        for i in range(len_value):
            item_index = i % self.max_items_on_page
            button_topleft = (
                ((TILE_SIZE + self.margin) * item_index) + self.margin * 2, WINDOW_HEIGHT - self.rect.height
            )
            button_rect = pygame.Rect(button_topleft, (TILE_SIZE, TILE_SIZE))
            buttons_list.append(button_rect)
        return buttons_list

    def create_animations(self):
        """
        Create animations for the menu items.
        """
        self.animations = {}
        for k, v in self.menu_surfs.items():
            self.animations[k] = []
            for key, value in EDITOR_DATA.items():
                if value['menu'] == k:
                    if value['graphics'] is None:
                        self.animations[k].append({key: None})
                    else:
                        paths = self.get_files_in_directory(value['graphics'])
                        images = [load(path).convert_alpha() for path in paths]
                        self.animations[k].append({key: images})

    def create_buttons(self):
        """
        Create buttons for the menu.
        """
        # Menu area setup
        self.margin = MENU_MARGIN
        self.max_items_on_page = (WINDOW_WIDTH - (self.margin * 3)) // (TILE_SIZE + self.margin)
        self.margin = (WINDOW_WIDTH - (TILE_SIZE * self.max_items_on_page)) / (self.max_items_on_page + 3)

        size = TILE_SIZE + (self.margin * 2)
        self.topleft = (self.margin, WINDOW_HEIGHT - self.margin - size)
        topright = (WINDOW_WIDTH - (self.margin * 2), size)

        self.rect = pygame.Rect(self.topleft, topright)
        self.shape_surf = pygame.Surface(pygame.Rect(self.rect.inflate(4, 4)).size, pygame.SRCALPHA)
        pygame.draw.rect(self.shape_surf, MENU_LINE_COLOR, self.shape_surf.get_rect(), border_radius=4)

        self.tile_button_rect = pygame.Rect((0, 0), (TILE_SIZE, TILE_SIZE))

        # Button areas setup
        self.button_rects = self.create_rects(len(self.menu_surfs))
        self.items_rects = self.create_rects(self.max_items_on_page)

        self.create_animations()

        # Create buttons
        self.buttons = pygame.sprite.Group()

        for i, key in enumerate(self.menu_surfs):
            Button(self.button_rects[i], self.buttons, self.menu_surfs[key], self.items_rects, self.animations[key])

    def click(self, mouse_pos, mouse_buttons, page, inner_page):
        """
        Handle mouse click events for the menu.

        Args:
            mouse_pos (tuple): The current mouse position.
            mouse_buttons (tuple): The current state of the mouse buttons.
            page (int): The current page number.
            inner_page (int): The current inner page number.

        Returns:
            tuple: The selected index, inner selection index, and page number.
        """
        inner_selection_index = None

        if self.inner_mode:
            max_index_value = self.max_inner_items
            for i, rect in enumerate(self.inner_sprite.inner_rects):
                if rect.collidepoint(mouse_pos):
                    if mouse_buttons[0]:
                        inner_selection_index = i + (self.max_items_on_page * (inner_page - 1))

                        if inner_selection_index >= max_index_value:
                            inner_selection_index = None
                        elif inner_selection_index >= self.max_items_on_page:
                            inner_selection_index -= (self.max_items_on_page * (inner_page - 1))

                    if mouse_buttons[2] or mouse_buttons[1]:
                        self.inner_sprite.change_mode()
                        self.inner_mode = False

                    return None, inner_selection_index, None

        for i, sprite in enumerate(self.buttons):
            if self.start_page <= i <= self.end_page:
                if not self.inner_mode and sprite.rect.collidepoint(mouse_pos):
                    # Find the nearest number in self.indexes to sprite.get_id()
                    sprite_id = sprite.get_id()
                    nearest_index = self.indexes.index(min(self.indexes, key=lambda x: abs(x - sprite_id)))

                    if mouse_buttons[1]:
                        self.inner_mode = not self.inner_mode
                        sprite.change_mode()
                        if self.inner_mode:
                            self.inner_sprite = sprite
                            self.max_inner_items = sprite.get_max_inner_items()

                    if mouse_buttons[2]:
                        sprite.switch()
                        sprite_id = sprite.get_id()
                        self.indexes[nearest_index] = sprite_id

                    return nearest_index, 0, 1

        return None, None, None

    def highlight_indicator(self, index, inner_index):
        """
        Highlight the selected button or inner item.

        Args:
            index (int): The index of the selected button.
            inner_index (int): The index of the selected inner item.
        """
        if self.inner_mode:
            rect = self.inner_sprite.inner_rects[inner_index]
        else:
            rect = next((sprite.get_rect() for sprite in self.buttons if sprite.get_id() == index), None)

        if rect:
            self.tile_button_rect.topleft = rect.topleft
            self.tile_button_rect.topright = rect.topright
            pygame.draw.rect(self.display_surface, BUTTON_LINE_COLOR, self.tile_button_rect.inflate(4, 4), 5, 4)

    def draw_buttons_on_page(self, page):
        """
        Draw the buttons on the current page.

        Args:
            page (int): The current page number.
        """
        if self.inner_mode:
            for i in range(self.max_items_on_page):
                self.display_surface.blit(self.inner_sprite.inner_images[i], self.items_rects[i])
            return

        if self.old_page != page:
            self.start_page = 0 if page == 1 else (self.max_items_on_page) * (page - 1)
            self.end_page = min(self.start_page + self.max_items_on_page - 1, len(self.buttons) - 1)
            self.old_page = page

        for i, sprite in enumerate(self.buttons):
            if self.start_page <= i <= self.end_page:
                self.display_surface.blit(sprite.image, sprite.rect)

    def display(self, index, inner_index, page, inner_page):
        """
        Display the menu and highlight the selected button or inner item.

        Args:
            index (int): The index of the selected button.
            inner_index (int): The index of the selected inner item.
            page (int): The current page number.
            inner_page (int): The current inner page number.
        """
        self.display_surface.blit(self.shape_surf, self.rect.inflate(4, 4))
        self.buttons.update(inner_page, self.max_items_on_page)
        self.draw_buttons_on_page(page)
        self.highlight_indicator(index, inner_index)


class Button(pygame.sprite.Sprite):
    def __init__(self, rect, group, items, inner_rects, animation=None):
        super().__init__(group)

        self.rect = rect
        self.image = pygame.Surface(self.rect.size)
        self.inner_rects = inner_rects
        self.animation = animation

        # Items
        self.items = items
        self.inner_images = []
        self.inner_images_to_draw = []

        self.index = 0
        self.inner_index = 0

        self.old_page = None
        self.old_index = None

        self.inner_mode = False

    def get_max_inner_items(self):
        """
        Get the maximum number of inner items.

        Returns:
            int: The number of inner items.
        """
        return len(self.items[self.index][2])

    def get_id(self):
        """
        Get the ID of the current item.

        Returns:
            int: The ID of the current item.
        """
        return self.items[self.index][0]

    def get_rect(self):
        """
        Get the rectangle of the button.

        Returns:
            pygame.Rect: The rectangle of the button.
        """
        return self.rect

    def switch(self):
        """Switch to the next item in the list."""
        self.index = (self.index + 1) % len(self.items)

    def change_mode(self):
        """Toggle the inner mode of the button."""
        self.inner_mode = not self.inner_mode

    def update(self, page, max_items):
        """
        Update the button's state.

        Args:
            page (int): The current page number.
            max_items (int): The maximum number of items per page.
        """
        if self.inner_mode:
            if page != self.old_page or self.index != self.old_index:
                self._update_inner_images(page, max_items)
                self.old_page = page
                self.old_index = self.index
            return

        self._update_main_image()

    def _update_inner_images(self, page, max_items):
        """
        Update the inner images of the button.

        Args:
            page (int): The current page number.
            max_items (int): The maximum number of items per page.
        """
        # Draw all inner items
        start_page = 0 if page == 1 else max_items * (page - 1)
        end_page = max_items * page

        # Clear old data
        self.inner_images = [pygame.Surface(self.rect.size, pygame.SRCALPHA) for _ in range(max_items)]
        self.inner_images_to_draw = [pygame.Surface(self.rect.size, pygame.SRCALPHA) for _ in range(max_items)]

        for i, surf in enumerate(self.items[self.index][2][start_page:end_page]):
            image = pygame.Surface(self.rect.size)
            image_to_draw = pygame.Surface(surf.get_size(), pygame.SRCALPHA)

            image.fill(BUTTON_BG_COLOR)
            rect = surf.get_rect(center=(self.rect.width * 0.5, self.rect.height * 0.5))
            rect_to_draw = surf.get_rect()
            image.blit(surf, rect)
            image_to_draw.blit(surf, rect_to_draw)

            self.inner_images[i] = image
            self.inner_images_to_draw[i] = image_to_draw

    def _update_main_image(self):
        """Update the main image of the button."""
        self.image.fill(BUTTON_BG_COLOR)
        surf = self.items[self.index][1]
        rect = surf.get_rect(center=(self.rect.width * 0.5, self.rect.height * 0.5))
        self.image.blit(surf, rect)
