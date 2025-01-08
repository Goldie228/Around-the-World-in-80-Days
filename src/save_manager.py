import pandas as pd
import json
import re
import os
import tkinter as tk
from tkinter import messagebox

from pygame.image import load
from glob import glob

from src.editor.settings import *


class SaveManager:
    def __init__(self, canvas_obj, collider_obj, is_editor):
        """
        Initialize the SaveManager.

        Args:
            canvas_obj: The canvas object.
            collider_obj: The collider object.
            is_editor (bool): Flag indicating if it's in editor mode.
        """
        self.canvas_obj = canvas_obj
        self.collider_obj = collider_obj
        self.is_editor = is_editor
        self.tile_size = None

    @staticmethod
    def _get_files_in_directory(directory_path):
        """
        Get a list of files in the specified directory.

        Args:
            directory_path (str): The path to the directory.

        Returns:
            list: A list of file paths.
        """
        parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        directory_path = os.path.join(parent_path, directory_path)
        items = os.listdir(directory_path)
        return [
            os.path.join(directory_path, item)
            for item in items
            if os.path.isfile(os.path.join(directory_path, item))
        ]

    @staticmethod
    def _get_relative_path(full_path: str) -> str:
        if not full_path:
            return

        current_dir = os.path.abspath(".")
        relative_path = os.path.relpath(full_path, current_dir)
        return relative_path

    @staticmethod
    def _get_start_cell_coordinates(cell):
        """
        Get the starting cell coordinates.

        Args:
            cell (tuple): The cell coordinates.

        Returns:
            tuple: The starting cell coordinates.
        """
        col, row = cell
        x = col // TILE_SIZE
        y = row // TILE_SIZE
        return x, y

    @staticmethod
    def _show_error(title, message):
        """
        Show an error message.

        Args:
            title (str): The title of the error message.
            message (str): The error message.
        """
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()

    @staticmethod
    def _get_start_free_pos_coordinates(cell):
        """
        Get the starting free position coordinates.

        Args:
            cell (tuple): The cell coordinates.

        Returns:
            tuple: The starting free position coordinates.
        """
        col, row = cell
        x = col * TILE_SIZE
        y = row * TILE_SIZE
        return x, y

    @staticmethod
    def _get_canvas_data_length(canvas_data):
        """
        Get the total length of the canvas data.

        Args:
            canvas_data (dict): The canvas data.

        Returns:
            int: The total length of the canvas data.
        """
        return sum(len(layer) for layer in canvas_data.values())

    def _find_index_and_inner_index(self, image_path):
        """
        Find the index and inner index of an image path.

        Args:
            image_path (str): The path to the image.

        Returns:
            tuple: The index and inner index of the image.
        """
        for index, data in EDITOR_DATA.items():
            if data['menu_surf'] and os.path.dirname(image_path).endswith(data['menu_surf']):
                paths = self._get_files_in_directory(data['menu_surf'])
                if image_path in paths:
                    inner_index = paths.index(image_path)
                    return index, inner_index
        return None, None

    def export_tiles(self, path, canvas_data):
        """
        Export the tile data to a CSV file.

        Args:
            path (str): The path to the CSV file.
            canvas_data (dict): The canvas data.
        """
        if not path or not canvas_data:
            print("path and canvas_data cannot be None or empty.")

        export_data = {
            'layer': [],
            'coords': [],
            'image_path': [],
            'animation_path': [],
            'is_item': [],
            'is_npc': [],
            'is_enemy': [],
            'is_player': [],
            'is_event': [],
            'id': [],
            'size': []
        }

        for layer in range(1, 15):
            for cell, canvas in canvas_data.get(layer, {}).items():
                pos = canvas.free_pos or self._get_start_free_pos_coordinates(cell)

                export_data['layer'].append(layer)
                export_data['coords'].append(json.dumps(pos))
                export_data['image_path'].append(self._get_relative_path(canvas.path_to_image or ''))
                export_data['animation_path'].append(self._get_relative_path(canvas.animation_dir or ''))
                export_data['is_item'].append(canvas.item)
                export_data['is_npc'].append(canvas.npc)
                export_data['is_enemy'].append(canvas.enemy)
                export_data['is_player'].append(canvas.player)
                export_data['is_event'].append(canvas.event)
                export_data['id'].append(canvas.id)
                export_data['size'].append(canvas.size)

        df = pd.DataFrame(export_data)
        df.to_csv(path, index=False)

    def export_colliders(self, path, collider_data):
        """
        Export the collider data to a CSV file.

        Args:
            path (str): The path to the CSV file.
            collider_data (dict): The collider data.
        """
        export_data = {
            'coords': [],
            'image_path': [],
            'collider_type': [],
        }

        for cell, collider in collider_data.items():
            pos = self._get_start_free_pos_coordinates(cell)

            export_data['coords'].append(json.dumps(pos))
            export_data['image_path'].append(self._get_relative_path(collider.path_to_image or ''))
            export_data['collider_type'].append(collider.collision_type)

        df = pd.DataFrame(export_data)
        df.to_csv(path, index=False)

    @staticmethod
    def export_settings(path):
        """
        Export the settings to a JSON file.

        Args:
            path (str): The path to the JSON file.
        """
        export_data = {
            'tile_size': TILE_SIZE,
            'animation_speed': ANIMATION_SPEED,
            'camera_speed_on_layer': CAMERA_SPEED_ON_LAYER,
            'sky_color': SKY_COLOR,
            'horizon_color': HORIZON_COLOR,
            'horizon_top_color': HORIZON_TOP_COLOR
        }

        # Convert the data into JSON format with the required formatting
        json_str = json.dumps(export_data, indent=4, ensure_ascii=False)

        # Use regular expressions to convert arrays into one string
        json_str = re.sub(r'\[\s*(\d+),\s*(\d+)\s*\]', r'[\1, \2]', json_str)

        # Write formatted JSON to a file
        with open(path, 'w', encoding='utf-8') as json_file:
            json_file.write(json_str)

    def import_tiles(self, path):  # Sourcery skip: avoid-builtin-shadow
        """
        Import tile data from a CSV file.

        Args:
            path (str): The path to the CSV file.

        Returns:
            dict: The imported canvas data.
        """
        df = pd.read_csv(path)
        image_cache = {}  # Dictionary for caching images
        animation_cache = {}  # Dictionary for caching animations
        canvas_data = {i: {} for i in range(15)}

        for i in range(len(df)):
            layer = df['layer'][i]
            coords = tuple(json.loads(df['coords'][i]))
            image_path = df['image_path'][i]
            animation_path = df['animation_path'][i]
            is_item = df['is_item'][i]
            is_npc = df['is_npc'][i]
            is_enemy = df['is_enemy'][i]
            is_player = df['is_player'][i]
            is_event = df['is_event'][i]
            id = df['id'][i]
            id = id if pd.notna(id) else None

            # Convert size from string to tuple of integers
            size_str = df['size'][i]
            size = tuple(map(int, size_str.strip('()').split(',')))

            cell = self._get_start_cell_coordinates(coords)

            # Find index and inner index
            index, inner_index = self._find_index_and_inner_index(image_path)

            # Load image using cache
            if image_path not in image_cache:
                try:
                    image_cache[image_path] = load(image_path).convert_alpha()
                except Exception as e:
                    image_cache[image_path] = load('assets\\graphics\\texture_error\\error.png').convert_alpha()  # Замените на путь к базовому изображению
            image = image_cache[image_path]

            # Load animation using cache if animation_path is not NaN
            animation = None
            if pd.notna(animation_path):
                if animation_path not in animation_cache:
                    animation_files = sorted(glob(os.path.join(animation_path, '*.png')))
                    animation_cache[animation_path] = tuple(load(file).convert_alpha() for file in animation_files)
                animation = animation_cache[animation_path]

            # Create CanvasObject and set attributes
            if self.is_editor:
                canvas_obj = self.canvas_obj(
                    index=index,
                    inner_index=inner_index,
                    tile=cell,
                    layer=layer,
                    image=image,
                    image_path=image_path,
                    free_pos=coords,
                    animation=animation
                )
            else:
                canvas_obj = self.canvas_obj(
                    layer=layer,
                    image=image,
                    pos=coords,
                    animation=animation
                )

            canvas_obj.item = is_item
            canvas_obj.npc = is_npc
            canvas_obj.enemy = is_enemy
            canvas_obj.player = is_player
            canvas_obj.event = is_event
            canvas_obj.size = size
            canvas_obj.id = id

            # Add canvas_obj to canvas_data
            canvas_data[layer][coords] = canvas_obj

        return canvas_data

    def import_colliders(self, path):
        """
        Import collider data from a CSV file.

        Args:
            path (str): The path to the CSV file.

        Returns:
            dict: The imported collider data.
        """
        df = pd.read_csv(path)
        image_cache = {}  # Dictionary for caching images
        collider_data = {}

        for i in range(len(df)):
            coords = tuple(json.loads(df['coords'][i]))
            image_path = df['image_path'][i]
            collider_type = df['collider_type'][i]

            # Find index and inner index
            index, inner_index = self._find_index_and_inner_index(image_path)
            cell = self._get_start_cell_coordinates(coords)

            # Load image using cache
            if image_path not in image_cache:
                image_cache[image_path] = load(image_path).convert_alpha()
            image = image_cache[image_path]

            # Create CanvasObject and set attributes
            if self.is_editor:
                collider_obj = self.canvas_obj(
                    index=index,
                    inner_index=inner_index,
                    inner_mode=False,  # Set inner_mode if needed
                    layer=9,
                    image=image,  # Use cached image
                    image_path=image_path,
                    free_pos=coords,
                    animation=None  # Colliders don't use animation
                )

                collider_obj.collision_type = collider_type

                collider_data[cell] = collider_obj
            else:
                collider_obj = self.collider_obj(
                    layer=9,
                    pos=coords,
                    collider_type=collider_type,
                    size=self.tile_size
                )

                collider_data[coords] = collider_obj

        return collider_data

    def import_settings(self, path):
        """
        Import settings from a JSON file.

        Args:
            path (str): The path to the JSON file.

        Returns:
            dict: The imported settings data.
        """
        with open(path, 'r', encoding='utf-8') as json_file:
            json_str = json_file.read()

        # Use regular expressions to convert arrays back into lists
        json_str = re.sub(r'\[\s*(\d+),\s*(\d+)\s*\]', r'[\1, \2]', json_str)
        data = json.loads(json_str)

        self.tile_size = data['tile_size']

        return data

    def export_scene(self, dir_path, filename, canvas_data, collider_data):
        """
        Export the entire scene to a directory.

        Args:
            dir_path (str): The directory path.
            filename (str): The filename for the scene.
            canvas_data (dict): The canvas data.
            collider_data (dict): The collider data.
        """
        if not dir_path or not filename:
            print('Save Error')
            return

        dir_path = os.path.join(dir_path, filename)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        tiles_path = os.path.join(dir_path, 'tiles.csv')
        self.export_tiles(tiles_path, canvas_data)

        colliders_path = os.path.join(dir_path, 'colliders.csv')
        self.export_colliders(colliders_path, collider_data)

        settings_path = os.path.join(dir_path, 'settings.json')
        self.export_settings(settings_path)

    def import_scene(self, dir_path, filename):
        """
        Import the entire scene from a directory.

        Args:
            dir_path (str): The directory path.
            filename (str): The filename for the scene.

        Returns:
            list: The imported scene data.
        """
        data = []

        # Import tiles
        path = os.path.join(dir_path, filename, 'tiles.csv')
        if os.path.exists(path):
            data.append(self.import_tiles(path))
        else:
            return None

        # Import settings
        path = os.path.join(dir_path, filename, 'settings.json')
        if os.path.exists(path):
            data.append(self.import_settings(path))
        else:
            return None

        # Import colliders
        path = os.path.join(dir_path, filename, 'colliders.csv')
        if os.path.exists(path):
            data.append(self.import_colliders(path))
        else:
            return None

        return data
