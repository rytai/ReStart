import pygame

__author__ = 'Kodex'

class Resource_Loader():

    # 64x64 character/item sprite
    sprites = {
        'hero': 'dg_classm32_swordHero.gif',
        'thug': 'dg_monster132_thug.gif',

        'sword': 'dg_weapons32_sword.gif'
    }

    map_tiles = {
        1: ('dg_features32_floor.gif', True),
        2: ('dg_extra132_boulderFloor.gif', False),
    }

    loaded_sprites = {}
    map_tiles_loaded = False

    def __init__(self):
        self.map_tiles_loaded = False


    def load_sprite(self, key):
        """
        Return either instance of surface

        :type key: str
        :rtype : (pygame.Surface, pygame.Rect)
        """

        # Sprite has been loaded to the dict
        try:
            if self.sprites[key] == 'Sprite_loaded':
                return self.loaded_sprites[key]
            else:
                new_sprite = pygame.image.load(self.sprites[key])
        except KeyError:
            print 'ResourceLoader Error: No sprite keyed: {}'.format(key)
            return None

        assert isinstance(new_sprite, pygame.Surface)
        new_sprite = pygame.transform.scale(new_sprite, (64, 64))
        new_sprite.set_colorkey((255, 255, 255))  # White

        self.sprites[key] = 'Sprite_loaded'
        self.loaded_sprites[key] = new_sprite

        return new_sprite

    @property
    def get_tilesheet(self):
        """Palauttaa dictionaryn. avaimet alkaa ykkosesta
        :rtype dict"""

        if self.map_tiles_loaded == False:
            for id, file_path_passable in self.map_tiles.items():
                file_path, passable = file_path_passable
                new_surface = pygame.image.load(file_path)
                new_surface = pygame.transform.scale(new_surface, (64, 64))
                self.map_tiles[id] = new_surface, passable

                self.map_tiles_loaded = True

        return self.map_tiles