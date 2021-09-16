#Third Party Libraries / Toolkits
import socket
import threading
import configparser
import gi; gi.require_version("Gtk", "4.0"); from gi.repository import Gt
#First Party Modules

#Main Variable Setup

#GUI Setup
window = Gtk.Window()
win.connect("destroy", gtk.main_quit)
win.show_all()
gtk.main()

#Server Initalisation