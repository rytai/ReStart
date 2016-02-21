# coding=utf-8
import pygame
import os

__author__ = 'Kodex'


class Resource_Loader():
    # 64x64 character/item sprite
    sprites = {
        'hero': 'dg_classm32_swordHero.gif',
        'thug': 'dg_monster132_thug.gif',

        'sword': 'dg_weapons32_sword.gif'
    }
    sprites_folder = os.path.join('Resources', 'Sprites')

    map_tiles = {
        1: ('dg_features32_floor.gif', True),
        2: ('dg_extra132_boulderFloor.gif', False),
    }
    map_tiles_folder = os.path.join('Resources', 'Sprites')

    loaded_sprites = {}
    map_tiles_loaded = False

    #  ID: (filename, in_pieces)
    frames = {1: ('frame_default', True), 2: ('frame_default_whole', False)}
    frame_folder = os.path.join('Resources', 'Frames')

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
                sprite_file_path = os.path.join(self.sprites_folder, self.sprites[key])
                new_sprite = pygame.image.load(sprite_file_path)
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
                file_path = os.path.join(self.map_tiles_folder, file_path)
                new_surface = pygame.image.load(file_path)
                new_surface = pygame.transform.scale(new_surface, (64, 64))
                self.map_tiles[id] = new_surface, passable

                self.map_tiles_loaded = True

        return self.map_tiles

    def get_frame_pieces(self, frame_id_int):
        """Frame koostuu kahdeksasta osasta.
        Palautetaan lista alkaen vasemmasta yläreunasta myötäpäivään"""
        #Framea ei ole ladattu
        # From bits
        if self.frames[frame_id_int][1] == True:
            try:
                frame_pieces = []
                frame_filename = self.frames[frame_id_int][0]
                frame_pieces.append(os.path.join(self.frame_folder, frame_filename + '_topleft.png'))
                frame_pieces.append(os.path.join(self.frame_folder, frame_filename + '_top.png'))
                frame_pieces.append(os.path.join(self.frame_folder, frame_filename + '_topright.png'))
                frame_pieces.append(os.path.join(self.frame_folder, frame_filename + '_right.png'))
                frame_pieces.append(os.path.join(self.frame_folder, frame_filename + '_botright.png'))
                frame_pieces.append(os.path.join(self.frame_folder, frame_filename + '_bot.png'))
                frame_pieces.append(os.path.join(self.frame_folder, frame_filename + '_botleft.png'))
                frame_pieces.append(os.path.join(self.frame_folder, frame_filename + '_left.png'))
                self.frames[frame_id_int] = frame_pieces
                self.load_frame(frame_id_int, True)

            except TypeError, error:  # Frame on ladattu
                print error

            return self.frames[frame_id_int]
        else:  # Whole image
            self.frames[frame_id_int] = os.path.join(self.frame_folder, str(self.frames[frame_id_int][0]) + '.png')
            self.load_frame(frame_id_int, False)
            return self.frames[frame_id_int]

    def load_frame(self, frame_id, in_pieces):
        if in_pieces:
            self.frames[frame_id] = [pygame.image.load(file_path) for file_path in self.frames[frame_id]]
            for frame_bit in self.frames[frame_id]:
                frame_bit.convert()
        else:
            self.frames[frame_id] = pygame.image.load(self.frames[frame_id]).convert()
            self.frames[frame_id].set_colorkey((255, 255, 255))
