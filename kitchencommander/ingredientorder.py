__author__ = 'dominik'


class IngredientOrder(object):

    def __init__(self, ingredient):
        self.__ingredient = ingredient
        self.__delete_time = None

    @property
    def ingredient(self):
        return self.__ingredient

    @property
    def delete_time(self):
        return self.__delete_time

    @delete_time.setter
    def delete_time(self, delete_time):
        self.__delete_time = delete_time