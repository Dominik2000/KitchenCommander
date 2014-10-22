__author__ = 'dominik'

import xmlrpc.server
import threading


class RPCServerThread(threading.Thread):
    def __init__(self, ingredient_queue, ingredients, port):
        threading.Thread.__init__(self)
        self.server = xmlrpc.server.SimpleXMLRPCServer(("0.0.0.0", int(port)))
        self.server.register_function(self.add_ingredient, "add_to_queue")
        self.server.register_function(self.get_ingredients, "get_ingredients")
        self.ingredient_queue = ingredient_queue
        self.ingredients = ingredients
        self.ingredients_simple = {}
        for key in self.ingredients.keys():
            self.ingredients_simple[str(key)] = str(self.ingredients[key].ingredient_name)

    def run(self):
        self.server.serve_forever()

    def stop(self):
        print("Shutting down RPC server.")
        self.server.shutdown()

    def add_ingredient(self, ingredient_id):
        self.ingredient_queue.put(ingredient_id)
        return ingredient_id

    def get_ingredients(self):
        return self.ingredients_simple