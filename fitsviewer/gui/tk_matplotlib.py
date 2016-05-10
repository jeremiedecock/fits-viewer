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

DEFAULT_COLOR_MAP = "gnuplot2" # "gray"

# histogram types : [‘bar’ | ‘barstacked’ | ‘step’ | ‘stepfilled’]
HISTOGRAM_TYPE = 'bar'

#IMAGE_INTERPOLATION = 'bilinear'   # "smooth" map
IMAGE_INTERPOLATION = 'nearest'    # "raw" (non smooth) map

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

        self.file_path = None
        self.image_array = None

        # Matplotlib ##################

        self.fig = plt.figure(figsize=(8.0, 8.0))

        # Gui parameters ##############

        self._color_map = tk.StringVar()
        self._show_color_bar = tk.BooleanVar()
        self._show_image = tk.BooleanVar()
        self._show_histogram = tk.BooleanVar()

        # Make widgets ################

        self.root = root

        # Add a callback on WM_DELETE_WINDOW events
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        ## Buttons
        #quit_button = tk.Button(master=self.root, text='Quit', command=self.quit)
        #quit_button.pack(fill="x", expand=True)

        # Make a menubar ##############

        # Create a toplevel menu
        menubar = tk.Menu(self.root)

        # Create a pulldown menu: /File
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", command=self.select_fits_file)
        file_menu.add_command(label="Close", command=self.close_fits_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        menubar.add_cascade(label="File", menu=file_menu)

        # Create a pulldown menu: /View
        view_menu = tk.Menu(menubar, tearoff=0)

        view_menu.add_checkbutton(label="Show color bar",
                                  variable=self._show_color_bar,
                                  command=self.draw_figure)

        view_menu.add_checkbutton(label="Show image",
                                  variable=self._show_image,
                                  command=self.draw_figure)

        view_menu.add_checkbutton(label="Show histogram",
                                  variable=self._show_histogram,
                                  command=self.draw_figure)

        menubar.add_cascade(label="View", menu=view_menu)

        # Create a pulldown menu: /View/Color Map
        colormap_menu = tk.Menu(view_menu, tearoff=0)

        for cmap_str in get_colour_map_list():
            colormap_menu.add_radiobutton(label=cmap_str,
                                          variable=self._color_map,
                                          value=cmap_str,
                                          command=self.draw_figure)

        view_menu.add_cascade(label="Color Map", menu=colormap_menu)

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
        self.fig.canvas.draw()


    def draw_figure(self):
        if self.image_array is not None:
            self.fig.clf() # TODO
            
            if self.show_histogram and self.show_image:

                ax1 = self.fig.add_subplot(121)
                ax2 = self.fig.add_subplot(122)

                self._draw_histogram(ax1)
                self._draw_image(ax2)

            elif self.show_histogram or self.show_image:

                ax1 = self.fig.add_subplot(111)

                if self.show_histogram:
                    self._draw_histogram(ax1)
                else:
                    self._draw_image(ax1)

            self.fig.canvas.draw()


    def _draw_histogram(self, axis):

            #axis.set_title(self.file_path)

            # nparray.ravel(): Return a flattened array.
            values, bins, patches = axis.hist(self.image_array.ravel(),
                                              histtype=HISTOGRAM_TYPE,
                                              bins=self.image_array.max() - self.image_array.min(),
                                              #range=(0., 255.),
                                              fc='k',
                                              ec='k')

            axis.set_xlim([self.image_array.min(), self.image_array.max()])


    def _draw_image(self, axis):

            im = axis.imshow(self.image_array,
                             origin='lower',
                             interpolation=IMAGE_INTERPOLATION,
                             cmap=self.color_map)

            #axis.set_axis_off()

            if self.show_color_bar:
                plt.colorbar(im) # draw the colorbar


    # PROPERTIES ##############################################################

    @property
    def show_color_bar(self):
        return self._show_color_bar.get()

    @show_color_bar.setter
    def show_color_bar(self, value):
        self._show_color_bar.set(value)

    ###

    @property
    def show_image(self):
        return self._show_image.get()

    @show_image.setter
    def show_image(self, value):
        self._show_image.set(value)

    ###

    @property
    def show_histogram(self):
        return self._show_histogram.get()

    @show_histogram.setter
    def show_histogram(self, value):
        self._show_histogram.set(value)

    ###

    @property
    def color_map(self):
        return self._color_map.get()

    @color_map.setter
    def color_map(self, value):
        self._color_map.set(value)


def main():

    root = tk.Tk()   # TODO ?
    gui = TkGUI(root)

    # PARSE OPTIONS ###########################################################

    parser = argparse.ArgumentParser(description="Display a FITS file.")

    parser.add_argument("--cmap", "-C", default=DEFAULT_COLOR_MAP, metavar="STRING",
            help="the colormap to use. The list of available color maps is available here: "
                 "http://matplotlib.org/examples/color/colormaps_reference.html")

    parser.add_argument("--hidecbar", "-c", action="store_true",
            help="hide the color bar")

    parser.add_argument("--hideimage", "-i", action="store_true",
            help="hide the image")

    parser.add_argument("--showhist", "-H", action="store_true",
            help="show the histogram of the image")

    parser.add_argument("filearg", nargs="?", metavar="FILE", const=None,
            help="the FITS file to process")

    args = parser.parse_args()

    input_file_path = args.filearg

    # SET OPTIONS #############################################################

    gui.color_map = args.cmap
    gui.show_color_bar = not args.hidecbar
    gui.show_image = not args.hideimage
    gui.show_histogram = args.showhist

    if input_file_path is not None:
        gui.open_fits_file(input_file_path)

    # LAUNCH THE MAIN LOOP ####################################################

    gui.run()

if __name__ == "__main__":
    main()


