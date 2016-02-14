import pygame

__author__ = 'Kodex'
# 64x64 character/item sprite
sprites = {
    'hero' : 'dg_classm32_swordHero.gif',
    'thug' : 'dg_monster132_thug.gif',

    'sword' : 'dg_weapons32_sword.gif'
}

loaded_sprites = {}


def load_sprite(key):
    """
    Return either instance of surface

    :type key: str
    :rtype : (pygame.Surface, pygame.Rect)
    """

    # Sprite has been loaded to the dict
    try:
        if sprites[key] == 'Sprite_loaded':
            return loaded_sprites[key]
        else:
            new_sprite =  pygame.image.load(sprites[key])
    except KeyError:
        print 'ResourceLoader Error: No sprite keyed: {}'.format(key)
        return None

    
    assert isinstance(new_sprite, pygame.Surface)    
    new_sprite = pygame.transform.scale(new_sprite, (64, 64))
    new_sprite.set_colorkey((255,255,255)) # White

    sprites[key] = 'Sprite_loaded'
    loaded_sprites[key] = new_sprite
    
    return new_sprite