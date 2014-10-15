__author__ = 'dominik'

from gi.repository import Gtk
import configparser
import server

config = configparser.ConfigParser()
config.read('settings.cfg')

if config.get('General', 'Type') == 'Server':
        images_path = config.get('General', 'ImagesPath')
        ingredients_file = config.get('General', 'IngredientFile')
        server_window = server.Server(images_path, ingredients_file)
        server_window.connect("delete-event", Gtk.main_quit)
        server_window.show_all()
        Gtk.main()


