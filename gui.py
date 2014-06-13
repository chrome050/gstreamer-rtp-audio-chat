#!/usr/bin/python
import sys
import pygtk
import gtk
import socket
from receive import Receive
from send import Send


class Gui:
    send=Send()
    receive=Receive()
    def on_ptt_toggled(self, button, name):
        if button.get_active():
            self.send.start()
            print "PTT on"
        else:
            self.send.stop()
            print "PTT off"

    def on_quit_clicked(self, button, name):
            self.receive.quit()
            self.send.quit()
            gtk.main_quit()

    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def enter_callback(self, widget, entry):
        entry_text = entry.get_text()
        print "Entry contents: %s\n" % entry_text

    def __init__(self):
        
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        # Set the window title
        self.window.set_title("Audio Chat")
        
        # Set a handler for delete_event, that exit Gtk
        self.window.connect("delete_event", self.delete_event)

        # Sets the border width of the window.
        self.window.set_border_width(20)

        # Create a vertical box
        vbox = gtk.VBox(True, 2)

        # Put the vbox in the main window
        self.window.add(vbox)

        # Create the ptt button
        button = gtk.ToggleButton("PTT")

        # When the button is toggled, we call the "callback" method
        # with a pointer to "button" as its argument
        button.connect("toggled", self.on_ptt_toggled, "ptt")

        # Insert PTT button
        vbox.pack_start(button, True, True, 2)

        button.show()

        # Create "Quit" button
        button = gtk.Button("Quit")

        # If the button is clicked, we call the main_quit function
        button.connect("clicked", self.on_quit_clicked, "quit")

        # Insert the quit button
        vbox.pack_start(button, True, True, 2)

        # Entry
        entry = gtk.Entry(50)
        entry.connect("activate", self.enter_callback, entry)
        entry.set_text("Dst IP")
        entry.select_region(0, len(entry.get_text()))
        vbox.pack_start(entry, gtk.TRUE, gtk.TRUE, 0)


        entry.show()
        button.show()
        vbox.show()
        self.window.show()

        # Start receiver pipe
        self.receive.start()

def main():
    gtk.main()
    return 0


if __name__ == "__main__":
        Gui()
        main()

