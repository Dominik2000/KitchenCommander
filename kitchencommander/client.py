__author__ = 'dominik'

import xmlrpc.client
import socket
import math

import ingredient


class Client(Gtk.Window):
    def __init__(self, ip, port, button_rows=2, button_columns=2):
        self.connection = "http://{0}:{1}/".format(ip, port)

        print('Setting up GUI...')
        Gtk.Window.__init__(self, title="KitchenCommander - Client")
        self.fullscreen()

        # hb = Gtk.HeaderBar()
        # hb.set_show_close_button(False)
        # hb.props.title = "KitchenCommander - Client"
        # hb.set_show_close_button(True)
        # self.set_titlebar(hb)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")

        self.button_prev_page = Gtk.Button()
        self.button_prev_page.set_size_request(50, 50)
        self.button_prev_page.add(Gtk.Arrow(Gtk.ArrowType.LEFT, Gtk.ShadowType.NONE))
        self.button_prev_page.connect("clicked", self._prev_page)
        box.add(self.button_prev_page)

        self.button_next_page = Gtk.Button()
        self.button_next_page.set_size_request(50, 50)
        self.button_next_page.add(Gtk.Arrow(Gtk.ArrowType.RIGHT, Gtk.ShadowType.NONE))
        self.button_next_page.connect("clicked", self._next_page)
        box.add(self.button_next_page)

        # hb.pack_start(box)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.main_box.pack_start(box, False, False, 0)

        self.main_box.get_settings().set_string_property('gtk-font-name', 'Tahoma 24', '')

        print("Loading ingredients...")
        self.ingredients = {}
        if not self._get_ingredients():
            exit(100)

        self.actual_page = 0
        self.pages_number = math.ceil(len(self.ingredients) / (button_rows * button_columns))

        self.pages = {}
        for i in range(0, self.pages_number):
            self.pages[i] = Gtk.Table(button_rows, button_columns, True)

        page = 0
        x = 0
        y = 0
        for key, value in sorted(self.ingredients.items()):
            button = Gtk.Button(value.ingredient_name)
            button.connect("clicked", self._new_order, key)
            self.pages[page].attach(button, x, x + 1, y, y + 1)

            x += 1
            if x >= button_columns:
                x = 0
                y += 1
                if y >= button_rows:
                    page += 1
                    x = 0
                    y = 0

        self.button_prev_page.set_sensitive(False)
        self.main_box.pack_start(self.pages[self.actual_page], True, True, 0)
        self.add(self.main_box)
        self.show_all()

    def _new_order(self, button, ingredient_id):
        try:
            proxy = xmlrpc.client.ServerProxy(self.connection)
            ordered_id = proxy.add_to_queue(ingredient_id)

            if not ordered_id == ingredient_id:
                print('ERROR: Wrong id returned.')
        except xmlrpc.client.Fault as err:
            print('ERROR: ' + err.faultString)
        except socket.error:
            print('ERROR: No server available on this ip!')

    def _next_page(self, button):
        old_page = self.actual_page
        self.actual_page += 1
        self.main_box.remove(self.pages[old_page])
        self.main_box.pack_start(self.pages[self.actual_page], True, True, 0)
        self._update_button_state()
        self.show_all()

    def _prev_page(self, button):
        old_page = self.actual_page
        self.actual_page -= 1
        self.main_box.remove(self.pages[old_page])
        self.main_box.pack_start(self.pages[self.actual_page], True, True, 0)
        self._update_button_state()
        self.show_all()

    def _update_button_state(self):
        if self.actual_page <= 0:
            self.button_prev_page.set_sensitive(False)
        else:
            self.button_prev_page.set_sensitive(True)
        if self.actual_page >= self.pages_number - 1:
            self.button_next_page.set_sensitive(False)
        else:
            self.button_next_page.set_sensitive(True)

    def _get_ingredients(self):
        try:
            proxy = xmlrpc.client.ServerProxy(self.connection)

            ingredients_simple = proxy.get_ingredients()
            for key, value in ingredients_simple.items():
                ingr = ingredient.Ingredient(value)
                self.ingredients[int(key)] = ingr
            return True
        except xmlrpc.client.Fault as err:
            print('ERROR: ' + err.faultString)
        except socket.error:
            print('ERROR: No server available on this ip!')
        return False
