__author__ = 'dominik'

import argparse

from gi.repository import Gtk

import server
import client


parser = argparse.ArgumentParser()
parser.add_argument('type', type=str)
args = parser.parse_args()

if args.type == 'server':
    print("Starting server...")
    server_window = server.Server()
    server_window.connect("delete-event", Gtk.main_quit)
    server_window.show_all()
elif args.type == 'client':
    print("Starting client...")
    client_window = client.Client()
    client_window.connect("delete-event", Gtk.main_quit)
    client_window.show_all()
Gtk.main()