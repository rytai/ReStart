# coding=utf-8
from pygame import Rect


class Window:
    """ Juuriluokka ikkunalle.
    Ikkuna piirretään ruudulle.
    Ikkunaan syötetään tiedot sitä luodessa, sekä niitä voi metodeilla muokata.
    """

    rect = None

    background_color = (255, 255, 255)
    background_image = None

    dialog_instance = None

    frame_id = None
    frame_surface = None

    def __init__(self, rect=None):
        """

        :rtype: Window
        """
        if not rect:
            self.rect = Rect(100, 100, 300, 300)

    def set_background_image(self, image):
        """Asettaa ikkunalle taustakuvan."""

        self.background_image = image

    def set_background_color(self, color):
        """Asettaa ikkunalle taustavärin"""

    @property
    def get_background(self):
        """

        :rtype: tuple, pygame.Surface
        """
        return self.background_color, self.background_image


    @property
    def get_frame_id(self):
        return self.frame_id

    def set_frame_id(self, id_):
        self.frame_id = id_

    @property
    def get_frame_surface(self):
        return self.frame_surface

    def set_frame_surface(self, surface):
        self.frame_surface = surface


class DialogWindow(Window):
    portrait_surface = None
    text_lines = ['', '', '', '']
    title = 'Default title.'

    def __init__(self):
        """

        :rtype: DialogWindow
        """
        Window.__init__(self)
        Window.dialog_instance = self

        self.rect = Rect(20, 670, 635, 820-670)
        self.frame_id = 1
        self.frame_surface = None

    @property
    def get_text_lines(self):
        return self.text_lines

    def set_text_lines(self, text_lines):
        """

        :type text_lines: [str]
        """
        self.text_lines = text_lines

    @property
    def get_title(self):
        return self.title

    def set_title(self, title):
        self.title = title

    @property
    def get_portrait_surface(self):
        return self.portrait_surface