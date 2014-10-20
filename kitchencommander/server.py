__author__ = 'dominik'

import datetime
import queue
import socket
import configparser

from gi.repository import Gtk, GdkPixbuf, GObject
from bs4 import BeautifulSoup

import rpcserverthread
import ingredient
import ingredientorder


class Server(Gtk.Window):
    def __init__(self, grid_width=960, grid_height=540):
        # Queue which orders are showed
        self.ingredient_orders = queue.deque(maxlen=4)
        #Queue which orders are should be showed if place
        self.ingredient_orders_buffer = queue.Queue()
        #Queue which order is new and appears as overlay
        self.ingredient_order_new = None

        config = configparser.ConfigParser()
        config.read('settings.cfg')
        self.seconds_to_show = config.get('General', 'SecondsShowOrder')
        self.seconds_to_show_big = config.get('General', 'SecondsShowNewOrderBig')
        self.images_path = config.get('General', 'ImagesPath')
        self.ingredients_file = config.get('General', 'IngredientFile')
        self.rpc_port = config.get('General', 'Port')
        self.grid_width = grid_width
        self.grid_height = grid_height

        print('Setting up GUI...')
        Gtk.Window.__init__(self, title="KitchenCommander - Server")
        self.fullscreen()
        self.main_grid = Gtk.Grid()
        self.main_grid.set_size_request(self.grid_width, self.grid_height)

        self.boxes = [Gtk.Image(), Gtk.Image(), Gtk.Image(), Gtk.Image()]
        self.main_grid.attach(self.boxes[0], 0, 0, 1, 1)
        self.main_grid.attach(self.boxes[1], 1, 0, 1, 1)
        self.main_grid.attach(self.boxes[2], 0, 1, 1, 1)
        self.main_grid.attach(self.boxes[3], 1, 1, 1, 1)

        self.overlay = Gtk.Overlay()
        self.add(self.overlay)
        self.overlay.add(self.main_grid)

        self.overlay.show_all()
        self.show_all()

        print("Loading ingredients...")
        self.ingredients = {}
        self._load_ingredients()

        print('Trying to start RPC server...l')
        self.rpc = rpcserverthread.RPCServerThread(self.ingredient_orders_buffer, self.ingredients, self.rpc_port)
        self.rpc.start()
        print('Started server, running on ' +
              [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in
               [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1] + ':' +
              self.rpc_port)

        print('Starting update timer')
        GObject.timeout_add_seconds(1, self._update)

    def _load_ingredients(self):
        handler = open(self.ingredients_file).read()
        soup = BeautifulSoup(handler)

        i = 0
        for item in soup.find_all("ingredient"):
            ingr = ingredient.Ingredient(item.find("name").string)
            file = self.images_path + item.find("image").string
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(file)
            pixbuf = GdkPixbuf.Pixbuf.scale_simple(pixbuf, self.overlay.get_allocation().width,
                                                   self.overlay.get_allocation().height,
                                                   GdkPixbuf.InterpType.BILINEAR)
            image = Gtk.Image()
            image.set_from_pixbuf(pixbuf)
            ingr.image = image
            ingr.image.set_halign(Gtk.Align.START)
            ingr.image.set_valign(Gtk.Align.START)
            pixbuf = GdkPixbuf.Pixbuf.scale_simple(pixbuf, self.overlay.get_allocation().width / 2,
                                                   self.overlay.get_allocation().height / 2,
                                                   GdkPixbuf.InterpType.BILINEAR)
            image = Gtk.Image()
            image.set_from_pixbuf(pixbuf)
            ingr.image_thumbnail = image
            self.ingredients[i] = ingr
            i += 1

    def _update(self):
        try:
            element = self.ingredient_orders.popleft()
            if element.delete_time > datetime.datetime.now():
                self.ingredient_orders.appendleft(element)
        except IndexError:
            pass
        if not len(self.ingredient_orders) == self.ingredient_orders.maxlen \
                and not self.ingredient_orders_buffer.empty() and not self.ingredient_order_new:
            ingredient_id = self.ingredient_orders_buffer.get()
            try:
                element = ingredientorder.IngredientOrder(self.ingredients[ingredient_id])
                element.delete_time = datetime.datetime.now() + datetime.timedelta(seconds=int(self.seconds_to_show))
                self.ingredient_orders.append(element)
                self.ingredient_order_new = element
                print('Added new ingredient order to show with deletion time '
                      + element.delete_time.strftime('%H:%M:%S') + ' and ingredient '
                      + element.ingredient.ingredient_name)
                self.overlay.add_overlay(self.ingredient_order_new.ingredient.image)
                self.overlay.show_all()
                GObject.timeout_add_seconds(int(self.seconds_to_show_big), self._remove_overlay)

            except KeyError:
                print('Cannot find id ' + str(ingredient_id) + ' in dictionary')
        for box in self.boxes:
            box.clear()
        i = 0
        while True:
            try:
                self.boxes[i].set_from_pixbuf(self.ingredient_orders[i].ingredient.image_thumbnail.get_pixbuf())
            except IndexError:
                break
            i += 1
        return True

    def _remove_overlay(self):
        self.overlay.remove(self.ingredient_order_new.ingredient.image)
        self.ingredient_order_new = None
        return False