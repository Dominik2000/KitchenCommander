__author__ = 'dominik'


class Ingredient(object):

    def __init__(self, ingredient_name):
        self.__ingredient_name = ingredient_name
        self.__image_thumbnail = None
        self.__image = None

    @property
    def ingredient_name(self):
        return self.__ingredient_name

    @property
    def image_thumbnail(self):
        return self.__image_thumbnail

    @image_thumbnail.setter
    def image_thumbnail(self, image_thumbnail):
        self.__image_thumbnail = image_thumbnail

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, image):
        self.__image = image