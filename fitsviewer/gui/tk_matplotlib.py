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

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib import cm

import tkinter as tk

import argparse
import json
import os

from astropy.io import fits

###############################################################################

CONFIG_FILE_NAME = ".fitsviewer.json"

LAST_OPENED_FILES_LIST_MAX_SIZE = 15

DEFAULT_COLOR_MAP = "gnuplot2" # "gray"

# histogram types : [‘bar’ | ‘barstacked’ | ‘step’ | ‘stepfilled’]
HISTOGRAM_TYPE = 'bar'

#IMAGE_INTERPOLATION = 'bilinear'   # "smooth" map
IMAGE_INTERPOLATION = 'nearest'    # "raw" (non smooth) map

###############################################################################

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

        self.hdu_list = None         # The current HDU list
        self.hdu_index = None        # The current HDU index
        self.last_opened_files = []

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
        self.menubar = tk.Menu(self.root)

        # Create a pulldown menu: /File #############################
        file_menu = tk.Menu(self.menubar, tearoff=0)

        # /File/Open
        file_menu.add_command(label="Open...", command=self.select_fits_file)

        # /File/Open Recent
        self.open_recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Open Recent", menu=self.open_recent_menu)

        # /File/Close
        file_menu.add_command(label="Close", command=self.close_fits_file)

        file_menu.add_separator()

        # /File/Exit
        file_menu.add_command(label="Exit", command=self.quit)

        self.menubar.add_cascade(label="File", menu=file_menu)

        # Create a pulldown menu: /HDU ##############################
        self.hdu_menu = tk.Menu(self.menubar, tearoff=0)

        self.menubar.add_cascade(label="HDU", menu=self.hdu_menu)

        # Init the HDU menu
        self.update_hdu_menu()

        # Create a pulldown menu: /View #############################
        view_menu = tk.Menu(self.menubar, tearoff=0)

        view_menu.add_checkbutton(label="Show color bar",
                                  variable=self._show_color_bar,
                                  command=self.draw_figure)

        view_menu.add_checkbutton(label="Show image",
                                  variable=self._show_image,
                                  command=self.draw_figure)

        view_menu.add_checkbutton(label="Show histogram",
                                  variable=self._show_histogram,
                                  command=self.draw_figure)

        self.menubar.add_cascade(label="View", menu=view_menu)

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
        self.root.config(menu=self.menubar)


    def load_config(self):
        """
        Load the user's configuration file.
        """

        # Check whether config_file_path is a directory
        if os.path.isdir(self.config_file_path):
            error_msg = "Error: please remove or rename the following direcory: " + os.path.abspath(self.config_file_path)
            raise Exception(error_msg) # TODO

        # Load the configuration file if it exists
        if os.path.isfile(self.config_file_path):
            with open(self.config_file_path, "r") as fd:
                json_dict = json.load(fd)

                if "last_opened_files" in json_dict:
                    self.last_opened_files = json_dict["last_opened_files"]
                    self.update_open_recent_menu()

                if (self.color_map is None) and ("color_map" in json_dict):
                    self.color_map = json_dict["color_map"]

                #if (self.show_color_bar is None) and ("show_color_bar" in json_dict):
                #    self.show_color_bar = json_dict["show_color_bar"]

                #if (self.show_image is None) and ("show_image" in json_dict):
                #    self.show_image = json_dict["show_image"]

                #if (self.show_histogram is None) and ("show_histogram" in json_dict):
                #    self.show_histogram = json_dict["show_histogram"]


    def save_config(self):
        """
        Save the current setup in the user's configuration file.
        """

        # Check whether config_file_path is a directory ###

        if os.path.isdir(self.config_file_path):
            error_msg = "Error: please remove or rename the following direcory: " + os.path.abspath(self.config_file_path)
            raise Exception(error_msg)

        # Make the JSON dictionary ########################

        json_dict = {}
        json_dict["last_opened_files"] = self.last_opened_files
        json_dict["color_map"] = self.color_map
        #json_dict["show_color_bar"] = self.show_color_bar
        #json_dict["show_image"] = self.show_image
        #json_dict["show_histogram"] = self.show_histogram

        # Save the JSON file ##############################

        with open(self.config_file_path, "w") as fd:
            json.dump(json_dict, fd, sort_keys=True, indent=4)


    def run(self):
        """
        Launch the main loop (Tk event loop).
        """

        # TODO ???
        self.root.mainloop()


    def quit(self):
        self.save_config()
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
                    ('FITS Files', '.fits .fit .fts .fits.gz .fit.gz .fts.gz'),
                    ('All Files', '.*')
                ]

        if (len(self.last_opened_files) > 0) and (os.path.isdir(os.path.dirname(self.last_opened_files[0]))):
            initial_directory = os.path.dirname(self.last_opened_files[0])
        else:
            initial_directory = os.path.expanduser("~")

        path = tk.filedialog.askopenfilename(parent=self.root,
                                             filetypes=FILE_TYPES,
                                             defaultextension='.fits',
                                             initialdir=initial_directory,
                                             #initialfile='demo.fits',  # optional
                                             title='Select your file')

        self.open_fits_file(path)


    def open_fits_file(self, file_path):
        """
        Open and display the given FITS file.
        """

        # READ THE INPUT FILE #################################################

        self.hdu_list = fits.open(file_path)     # open the FITS file
        self.hdu_index = 0

        self.root.title(self.file_path)
        self.draw_figure()

        # UPDATE THE "LAST OPEN FILE LIST" ####################################

        # Add the opened path to the beginning of the list (or move it to the beginning if it's already in the list)
        if file_path in self.last_opened_files:
            self.last_opened_files.remove(file_path)
        self.last_opened_files.insert(0, file_path)

        # Keep the N first elements (with N = LAST_OPENED_FILES_LIST_MAX_SIZE)
        self.last_opened_files = self.last_opened_files[:LAST_OPENED_FILES_LIST_MAX_SIZE]

        # UPDATE THE SOME MENUS ###############################################

        self.update_open_recent_menu()
        self.update_hdu_menu()


    def select_hdu(self, hdu_index):
        """
        Open and display the given HDU item.
        """
        if (self.hdu_list is not None) and (0 <= hdu_index < len(self.hdu_list)):
            self.hdu_index = hdu_index
            self.draw_figure()
        else:
            raise Exception("Internal error.")


    def update_hdu_menu(self):
        """
        Update the "HDU" menu.
        """
        # Remove all menu items
        self.hdu_menu.delete(0, 1000)  # TODO: hugly but it seems that tkinter doesn't have any special value to delete all items and doesn't offer any method to count the number of items...

        if self.hdu_list is not None:
            # Enable the "/HDU/Show HDU Info" menu
            self.menubar.entryconfig("HDU", state="normal")

            # Populate the "/HDU" menu (add one button per HDU of the opened file)
            for hdu_index, hdu in enumerate(self.hdu_list):
                # TODO
                if hdu.is_image:
                    _label = "HDU{} ({}D image {} {})".format(hdu_index,
                                                              hdu.data.ndim,
                                                              "x".join([str(dim) for dim in hdu.data.shape]),
                                                              hdu.data.dtype.name)
                else:
                    _label = "HDU{} (table)".format(hdu_index)
                # See:
                # - http://effbot.org/zone/tkinter-callbacks.htm
                # - http://stackoverflow.com/questions/728356/dynamically-creating-a-menu-in-tkinter-lambda-expressions
                # - http://stackoverflow.com/questions/938429/scope-of-python-lambda-functions-and-their-parameters
                # - http://stackoverflow.com/questions/19693782/callback-function-tkinter-button-with-variable-parameter
                self.hdu_menu.add_command(label=_label,
                                          command=lambda index=hdu_index: self.select_hdu(index))
        else:
            # Disable the "/HDU/Show HDU Info" menu
            self.menubar.entryconfig("HDU", state="disabled")


    def update_open_recent_menu(self):
        """
        Update the "File/Open Recent" menu.
        """

        # Remove all menu items
        self.open_recent_menu.delete(0, LAST_OPENED_FILES_LIST_MAX_SIZE + 2)

        # Add menu items
        for recent_file_str in self.last_opened_files:
            # See:
            # - http://effbot.org/zone/tkinter-callbacks.htm
            # - http://stackoverflow.com/questions/728356/dynamically-creating-a-menu-in-tkinter-lambda-expressions
            # - http://stackoverflow.com/questions/938429/scope-of-python-lambda-functions-and-their-parameters
            # - http://stackoverflow.com/questions/19693782/callback-function-tkinter-button-with-variable-parameter
            self.open_recent_menu.add_command(label=recent_file_str, # TODO: only display the filename, not the full path ?
                                              command=lambda file_path=recent_file_str: self.open_fits_file(file_path))

        # Add the "Clear Menu" item
        self.open_recent_menu.add_separator()
        self.open_recent_menu.add_command(label="Clear Menu", command=self.clear_last_opened_files)


    def clear_last_opened_files(self):
        """
        Clear the list of recent opened files.
        """
        self.last_opened_files = []
        self.update_open_recent_menu()


    def close_fits_file(self):
        self.hdu_list.close()
        self.hdu_list = None
        self.hdu_index = None
        self.clear_figure()
        self.update_hdu_menu()


    def clear_figure(self):
        self.fig.clf()
        self.fig.canvas.draw()


    def draw_figure(self):
        if self.hdu_list is not None:
            if 0 <= self.hdu_index < len(self.hdu_list):

                # Clear the figure ##############
                self.fig.clf() # TODO

                # Get the image #################
                hdu = self.hdu_list[self.hdu_index]

                if hdu.is_image:
                    # The current HDU is an image

                    # Get the image #############
                    if hdu.data.ndim <= 2:
                        image_array = hdu.data
                    elif hdu.data.ndim == 3:
                        image_array = hdu.data[0]                  # TODO
                    elif hdu.data.ndim == 4:
                        image_array = hdu.data[0][0]               # TODO
                    else:
                        raise Exception("Internal error.")
                    
                    # Show the figure ###########
                    if self.show_histogram and self.show_image:

                        ax1 = self.fig.add_subplot(121)
                        ax2 = self.fig.add_subplot(122)

                        self._draw_histogram(ax1, image_array)
                        self._draw_image(ax2, image_array)

                    elif self.show_histogram or self.show_image:

                        ax1 = self.fig.add_subplot(111)

                        if self.show_histogram:
                            self._draw_histogram(ax1, image_array)
                        else:
                            self._draw_image(ax1, image_array)
                else:
                    # The current HDU is a table

                    # TODO
                    ax1 = self.fig.add_subplot(111)

                    #ax1.text(0.5, 0.5, 'Table...', fontsize=15)
                    ax1.text(0.5, 0.5, 'Table...', ha='center', va='center', fontsize=15, transform=ax1.transAxes)

                    #ax1.set_xlim([0, 1])
                    #ax1.set_ylim([0, 1])
                    ax1.set_axis_off()

                self.fig.canvas.draw()
            else:
                raise Exception("Internal error.")


    def _draw_histogram(self, axis, image_array):

            #axis.set_title(self.file_path)

            # nparray.ravel(): Return a flattened array.
            values, bins, patches = axis.hist(image_array.ravel(),
                                              histtype=HISTOGRAM_TYPE,
                                              bins=image_array.max() - image_array.min(),
                                              #range=(0., 255.),
                                              fc='k',
                                              ec='k')

            axis.set_xlim([image_array.min(), image_array.max()])


    def _draw_image(self, axis, image_array):

            if image_array.ndim == 1:
                image_array = np.tile(image_array, (256, 1))  # TODO ?
                axis.get_yaxis().set_visible(False)

            im = axis.imshow(image_array,
                             origin='lower',
                             interpolation=IMAGE_INTERPOLATION,
                             cmap=self.color_map)

            #axis.set_axis_off()

            if self.show_color_bar:
                plt.colorbar(im) # draw the colorbar


    # PROPERTIES ##############################################################

    @property
    def file_path(self):
        _file_path = None
        if self.hdu_list is not None:
            _file_path = self.hdu_list.filename()
        return _file_path

    ###

    @property
    def config_file_path(self):
        home_path = os.path.expanduser("~")
        return os.path.join(home_path, CONFIG_FILE_NAME)

    ###

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

    gui.load_config()

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


