import map_stuff
import resources
import pygame
import sys


class Map_editor:

    def __init__(self, resource_loader_inst):
        assert isinstance(resource_loader_inst, resources.Resource_Loader)

        self.tilesheet = resource_loader_inst.get_tilesheet

    def draw_tilesheet_window(self, tilesheet_surface):

        # Calculate how many tiles can fit in one row. tile_size 64
        tilesheet_size = tilesheet_surface.get_size()
        tiles_in_row = tilesheet_size[0] / 64
        space_between_tiles = (tilesheet_size[0] % 64) / (tiles_in_row - 1)

        # Print the tile to layer by looping the dict
        index_of_tile_in_row = 1
        row_index = 0
        for key, value in self.tilesheet.items():

            tile_x_position = (index_of_tile_in_row - 1) * 64
            tile_y_position = row_index * 64
            if index_of_tile_in_row > 1:
                tile_x_position += space_between_tiles
            # Value [0] surface, value[1] passability
            tilesheet_surface.blit(value[0], (tile_x_position, tile_y_position))

            if index_of_tile_in_row == tiles_in_row:
                index_of_tile_in_row = 1
                row_index += 1

            index_of_tile_in_row += 1

        return tilesheet_surface

    def launch(self, map_data, screen):
        world_window_size = (64 * 13, 64 * 13)

        # Calculate map size
        assert isinstance(map_data, map_stuff.MapData)
        map_size = map_data.get_map_size
        map_screen_size = world_window_size # tile_value_to_screen_value(map_size)

        # Load surfaces
        world_window_surface = pygame.Surface((64*13, 64*13))
        floor_surface = pygame.Surface(map_size)
        inventory_surface = pygame.Surface(map_size)
        char_surface = pygame.Surface(map_size)

        surfaces = [world_window_surface, floor_surface, inventory_surface, char_surface]

        tilesheet_surface = pygame.Surface((385, 840))
        tilesheet_rect = tilesheet_surface.get_rect(topleft=(895,0))

        tilesheet_surface = self.draw_tilesheet_window(tilesheet_surface)

        tilecursor_pos = (1,1)

        # Clear all the events.
        pygame.event.clear()

        editor = True
        while editor:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        pass # Place tile
                    elif event.key == pygame.K_UP or event.key == pygame.K_KP8:
                        pass
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_KP2:
                        pass
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_KP4:
                        pass
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_KP6:
                        pass
                    elif event.key == pygame.K_TAB or event.key == pygame.K_ESCAPE:
                        editor = False

            screen.blit(tilesheet_surface, tilesheet_rect)

            pygame.display.flip()