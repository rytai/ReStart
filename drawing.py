from map_stuff import MapData
from pygame import Surface
from pygame import Rect
import pygame

__author__ = 'Kodex'


class DirtyDrawing:
    world_surface_redraw = None

    dirty_tiles = []

    def __init__(self, floor_surface, map_data_texture_layer):
        assert floor_surface is not None
        assert map_data_texture_layer is not None

        self.prepare_floor(floor_surface, map_data_texture_layer)

        self.world_surface_redraw = True

    def draw(self, screen, world_s, camera, floor_s, map_data):
        """
        :param camera: Camera-class instance
        :param world_s: The world surface
        :param screen: The screen surface
        :type floor_s: Surface
        :type map_data: MapData
        """

        # Redraw the whole world window
        if self.world_surface_redraw:
            self.redraw_world_surface(screen, world_s, camera, floor_s, map_data)

        # Draw only the changed parts of the world window
        else:
            self.update_world_window(screen, world_s, camera, floor_s, map_data)

    def issue_world_surface_redraw(self):
        self.world_surface_redraw = True

    def redraw_world_surface(self, screen, world_s, camera, floor_s, map_data):
        # Blit the floor surface to world_surface.
        """

        :param map_data: The map_data instance
        :param floor_s: The floor surface
        :param world_s: The world surface
        :param screen: The screen surface
        :type camera: Camera
        """
        world_s.blit(floor_s, (0, 0))
        # Loop items on map
        for tile_position, item_or_list in map_data.get_item_layer.items():
            position_on_world = world_pos_of_tile(tile_position)
            self.draw_items_on_tile(world_s, item_or_list, position_on_world)
        # Loop characters on map
        for entity in map_data.get_characters_on_map:
            world_s.blit(entity.surface, entity.rect.topleft)

        # Blit the world surface to screen
        camera_rectangle = camera.get_viewport_rect
        assert isinstance(camera_rectangle, Rect)
        screen.blit(world_s, (16, 16), area=world_rect_of_tile_rect(camera_rectangle))

        self.world_surface_redraw = False
        map_data.reset_dirty_tiles()

    def update_world_window(self, screen, world_s, camera, floor_s, map_data):
        blit_area = Rect(0, 0, 64, 64)
        # Get the dirty tile -coordinates from map_data
        for dirty_tile_position in map_data.get_dirty_tile_positions:
            # Calculate the screen position for given tile
            dirty_world_position = world_pos_of_tile(dirty_tile_position)

            area_x, area_y = dirty_tile_position
            blit_area.topleft = (area_x * 64, area_y * 64)

            # Blit the tile from floor, to screen.
            world_s.blit(floor_s, dirty_world_position, blit_area)
            # Blit items in the tile

            # Try if this position contains a list of items. Note: these may fail :s
            items_in_position = map_data.get_items_on_position(dirty_tile_position)
            if items_in_position is not None:
                self.draw_items_on_tile(world_s, items_in_position, dirty_world_position)

            # Blit character in here.
            character = map_data.get_character_on_position(dirty_tile_position)
            if character is not None:
                world_s.blit(character.surface, dirty_world_position)

            camera_rectangle = camera.get_viewport_rect
            assert isinstance(camera_rectangle, Rect)
            screen.blit(world_s, (16, 16), area=world_rect_of_tile_rect(camera_rectangle))

        map_data.reset_dirty_tiles()

    @staticmethod
    def draw_items_on_tile(screen, item_or_list, screen_position):
        try:
            for item in item_or_list:
                item_surface = item.surface
                if item_surface is not None:
                    screen.blit(item.surface, screen_position)
        # There's a single item. - (item object not iterable)
        except TypeError:
            item_surface = item_or_list.surface
            if item_surface is not None:
                screen.blit(item_surface, screen_position)

    @staticmethod
    def prepare_floor(floor_s, texture_layer):
        """
        :type floor_s: Surface
        :type texture_layer: dict
        """

        for position, texture in texture_layer.items():
            x_pos, y_pos = position[0] * 64, position[1] * 64
            floor_s.blit(texture, (x_pos, y_pos))

    @staticmethod
    def draw_message_log(screen, message_log):
        screen.blit(message_log.render, message_log.position)
        message_log.set_is_dirty(False)


def screen_position_of_tile(tile_position):
    """

    :param tile_position: tile coordinate tuple
    :rtype : tuple
    """
    return tile_position[0] * 64 + 16, tile_position[1] * 64 + 16


def world_pos_of_tile(tile_position):
    return tile_position[0] * 64, tile_position[1] * 64


def world_rect_of_tile_rect(tile_rectangle):
    assert tile_rectangle, Rect
    topleft = tile_rectangle.topleft
    topleft = topleft[0] * 64, topleft[1] * 64
    width = tile_rectangle.width * 64
    height = tile_rectangle.height * 64
    world_rect = Rect(topleft, (width, height))
    return world_rect


class TextBlit:
    def __init__(self, text_blit_area):
        self.surface = pygame.Surface(text_blit_area)
        self.default_font = pygame.font.get_default_font()
        assert isinstance(self.default_font, pygame.font.Font)

    def render_text(self, font=None, text='def', color=(255,255,255), bg_color=(0,0,0), position=(0,0)):
        if font is None:
            font = self.default_font
        new_render = font.render(text, False, color, bg_color)

        self.surface.blit(new_render, position)
