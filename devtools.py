import map_stuff
import resources
import pygame
import sys


class Map_editor:
    self.tile_cursor_pos = (0, 0)
    self.world_window_pos = (0, 0)
    
    self.tile_size = (64, 64)
    self.world_window_tiles = (15, 15)
    self.world_window_size = (0, 0)
    
    self.tile_picker = None
    
    def __init__(self, resource_loader_inst):
        assert isinstance(resource_loader_inst, resources.Resource_Loader)

        self.tilesheet = resource_loader_inst.get_tilesheet
        
        self.tile_picker = TilePicker((385, 840), self.tile_size)
        
        self.tile_cursor_pos = (0, 0)
        x, y = self.world_window_tiles
        sx, sy = self.tile_size
        self.world_window_size = (x * sx, y * sy)
        
    class TilePicker():
        self.surface = None
        def __init__(self, surface_size, tile_size, tilesheet):
    
            # Calculate how many tiles we can fit in one row of TilePicker.
            self.surface = pygame.Surface(surface_size)
            self.surface_size = self.surface.get_size()
            
            self.tilesheet = tilesheet
            
            self.tiles_in_row = self.surface_size[0] / self.tile_size[0]
            self.space_between_tiles = (self.surface_size[0] % self.tile_size[0]) / (self.tiles_in_row - 1)
    
            # Print the tile to layer by looping the dict
            index_of_tile_in_row = 1
            row_index = 0
            for key, value in self.tilesheet.items():
    
                tile_x_position = (index_of_tile_in_row - 1) * 64
                tile_y_position = row_index * 64
                if index_of_tile_in_row > 1:
                    tile_x_position += self.space_between_tiles
                # Value [0] surface, value[1] passability
                self.surface.blit(value[0], (tile_x_position, tile_y_position))
    
                if index_of_tile_in_row == tiles_in_row:
                    index_of_tile_in_row = 1
                    row_index += 1
    
                index_of_tile_in_row += 1
                
    class WorldWindow():
        surface = None
        surface_size = (0,0)
            def __init__(self, tiles, tile_size):
                self.surface_size = tiles[0]+tile_size[0], tiles[1]+tile_size[1]
                self.surface = pygame.Surface(self.surface_size)

    def launch(self, map_data, screen):
        world_window_size = (64 * 13, 64 * 13)

        # Calculate map size
        assert isinstance(map_data, map_stuff.MapData)
        map_size = map_data.get_map_size

        # Load surfaces
        world_window_surface = pygame.Surface((64 * 13, 64 * 13))
        floor_surface = pygame.Surface(map_size)
        inventory_surface = pygame.Surface(map_size)
        char_surface = pygame.Surface(map_size)

        surfaces = [world_window_surface, floor_surface, inventory_surface, char_surface]

        tilesheet_surface = pygame.Surface()
        tilesheet_rect = tilesheet_surface.get_rect(topleft=(895, 0))

        tilesheet_surface = self.draw_tilesheet_window(tilesheet_surface)

        # Clear all the events.
        pygame.event.clear()

        editor = True
        while editor:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        pass  # Place tile
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
            
    def cursor_move(direction_tuple):
        new_position = self.tile_cursor_pos[0]+direction_tuple[0], self.tile_cursor_pos[1]+direction_tuple[1]
        self.tile_cursor_pos = new_position
            
    def get_mouse_target():
        mouse_position = pygame.mouse.get_pos()
        
        

def mouse_position_to_caption():
    mouse_position = str(pygame.mouse.get_pos())
    pygame.display.set_caption(mouse_position)
    
    
def mouse_position_to_tile():
    mouse_position = pygame.mouse.get_pos()
