import map_stuff
import resources
import pygame
import sys


def launch_mapeditor(map_data, resource_loader):
    world_window_size = (64 * 13, 64 * 13)

    # Calculate map size
    assert isinstance(map_data, map_stuff.MapData)
    map_size = map_data.get_map_size
    map_screen_size = tile_value_to_screen_value(map_size)

    # Load surfaces
    world_window_surface = pygame.Surface((64*13, 64*13))
    floor_surface = pygame.Surface(map_size)
    inventory_surface = pygame.Surface(map_size)
    char_surface = pygame.Surface(map_size)

    surfaces = [world_window_surface, floor_surface, inventory_surface, char_surface]

    tilecursor_pos = (1,1)

    # Clear all the events.
    pygame.event.clear()

    editor = True
    while editor:
        for event in pygame.event.get()
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    pass # Place tile
                elif event.key == pygame.K_UP or event.key == pygame.K_KP8:
                    hero.intent.type = intent.MOVE
                    hero.intent.direction = (0, -1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_KP2:
                    hero.intent.type = intent.MOVE
                    hero.intent.direction = (0, 1)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_KP4:
                    hero.intent.type = intent.MOVE
                    hero.intent.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_KP6:
                    hero.intent.type = intent.MOVE
                    hero.intent.direction = (1, 0)