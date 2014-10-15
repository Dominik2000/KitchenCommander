__author__ = 'dominik'

import ingredientorder
import xmlrpc.server
import threading


class RPCServerThread(threading.Thread):

    def __init__(self, ingredient_queue):
        threading.Thread.__init__(self)
        self.server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8000))
        self.server.register_function(self.add_ingredient, "add_to_queue")
        self.ingredient_queue = ingredient_queue

    def run(self):
        self.server.serve_forever()

    def stop(self):
        print("Shutting down RPC server.")
        self.server.shutdown()

    def add_ingredient(self, ingredient_id):
        self.ingredient_queue.put(ingredient_id)
        return ingredient_id