#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# FITS Viewer

# The MIT License
#
# Copyright (c) 2016 Jeremie DECOCK (http://www.jdhp.org)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Documentation: http://docs.astropy.org/en/stable/io/fits/index.html

__all__ = ['TkGUI']

import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib import cm

import tkinter as tk

import argparse
import os

from astropy.io import fits

###############################################################################

def get_image_array_from_fits_file(file_path):
    
    hdu_list = fits.open(file_path)   # open the FITS file

    if len(hdu_list) != 1:
        raise Exception("The FITS file should contain only one HDU.")

    image_array = hdu_list[0].data    # "hdu.data" is a Numpy Array

    hdu_list.close()

    return image_array


def get_colour_map_list():
    """Return the list of the available colormaps."""
    return sorted(plt.cm.datad)

###############################################################################

class TkGUI:
    """
    TODO...
    """

    def __init__(self, root):
        """
        TODO...
        """

        # Matplotlib ##################

        self.fig = plt.figure(figsize=(8.0, 8.0))
        self.ax = self.fig.add_subplot(111)

        # Gui parameters ##############

        self.color_map = None

        self._show_color_bar = tk.BooleanVar()

        self.file_path = None
        self.image_array = None

        # Make widgets ################

        #self.root = tk.Tk()   # TODO
        self.root = root

        # Add a callback on WM_DELETE_WINDOW events
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Buttons
        quit_button = tk.Button(master=self.root, text='Quit', command=self.quit)
        quit_button.pack(fill="x", expand=True)

        # Make a menubar ##############

        # Create a toplevel menu
        menubar = tk.Menu(self.root)

        # Create a pulldown menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", command=self.select_fits_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        menubar.add_cascade(label="File", menu=file_menu)

        # Create a pulldown menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_checkbutton(label="Show color bar",
                                  variable=self._show_color_bar,
                                  command=self.draw_figure)

        menubar.add_cascade(label="View", menu=view_menu)

        # Display the menu
        # The config method is used to attach the menu to the root window. The
        # contents of that menu is used to create a menubar at the top of the root
        # window. There is no need to pack the menu, since it is automatically
        # displayed by Tkinter.
        self.root.config(menu=menubar)


    def run(self):
        """
        Launch the main loop (Tk event loop).
        """

        # TODO ???
        self.root.mainloop()


    def quit(self):
        self.root.quit()     # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
                             # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def select_fits_file(self):
        """
        Display a file dialog to select the FITS file to open.

        Return the path of the selected file.
        """

        # Check and parse the file

        # FILE_TYPES = [(label1, pattern1), (label2, pattern2), ...]
        FILE_TYPES = [
                    ('FITS Files', '.fits')
                ]

        HOME = os.path.expanduser("~")

        path = tk.filedialog.askopenfilename(parent=self.root,
                                             filetypes=FILE_TYPES,     # optional
                                             defaultextension='.fits', # optional
                                             initialdir=HOME,          # optional
                                             #initialfile='demo.fits',  # optional
                                             title='Select your file') # optional

        self.open_fits_file(path)


    def open_fits_file(self, file_path):
        """
        Open and display the given FITS file.
        """
        # READ THE INPUT FILE #################################################

        self.file_path = file_path
        self.image_array = get_image_array_from_fits_file(self.file_path)

        if self.image_array.ndim != 2:
            raise Exception("Unexpected error: the input FITS file should contain a 2D array.")

        self.root.title(self.file_path)
        self.draw_figure()


    def close_fits_file(self):
        self.file_path = None
        self.image_array = None
        self.clear_figure()


    def clear_figure(self):
        self.fig.clf()


    def draw_figure(self):
        self.fig.clf() # TODO
        self.ax = self.fig.add_subplot(111)

        #self.ax.set_title(self.file_path)

        im = self.ax.imshow(self.image_array,
                            origin='lower',
                            interpolation='nearest',
                            cmap=self.color_map)

        if self.show_color_bar:
            plt.colorbar(im) # draw the colorbar

        self.fig.canvas.draw()

    # PROPERTIES ##############################################################

    @property
    def show_color_bar(self):
        return self._show_color_bar.get()

    @show_color_bar.setter
    def show_color_bar(self, value):
        self._show_color_bar.set(value)


def main():

    root = tk.Tk()   # TODO
    gui = TkGUI(root)

    # PARSE OPTIONS ###########################################################

    parser = argparse.ArgumentParser(description="Display a FITS file.")

    parser.add_argument("--cmap", "-c", default="gray", metavar="STRING",
            help="the colormap to use. The list of available color maps is available here: "
                 "http://matplotlib.org/examples/color/colormaps_reference.html")

    parser.add_argument("--hidecbar", "-H", action="store_true",
            help="hide the color bar")

    parser.add_argument("filearg", nargs=1, metavar="FILE",
            help="the FITS file to process")

    args = parser.parse_args()

    input_file_path = args.filearg[0]

    # SET OPTIONS #############################################################

    gui.color_map = args.cmap
    gui.show_color_bar = not args.hidecbar

    gui.open_fits_file(input_file_path)

    # LAUNCH THE MAIN LOOP ####################################################

    gui.run()

if __name__ == "__main__":
    main()


