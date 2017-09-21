#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Documentation: http://docs.astropy.org/en/stable/io/fits/index.html

import argparse
from astropy.io import fits
import os

import PIL.Image as pil_img # PIL.Image is a module not a class...
import numpy as np


def load_image(input_file_path):
    """
    Load the 'input_file_path' and return a 2D numpy array of the image it contains.
    """
    image_array = np.array(pil_img.open(input_file_path).convert('L'))
    return image_array


def save_fits_file(image_array, output_file_path):
    """
    image_array is the image and it should be a 2D numpy array with values in
    the range [0,255].
    """

    # FLIP THE IMAGE IN THE UP/DOWN DIRECTION #############
    # WARNING: with fits, the (0,0) point is at the BOTTOM left corner
    #          whereas with pillow, the (0,0) point is at the TOP left corner
    #          thus the image should be converted

    image_array = np.flipud(image_array)

    # CREATE THE FITS STRUCTURE ###########################

    hdu = fits.PrimaryHDU(image_array)

    # SAVE THE FITS FILE ##################################

    # Save the FITS file (overwrite the file if it already exists)
    try:
        hdu.writeto(output_file_path, overwrite=True)
    except TypeError:
        hdu.writeto(output_file_path, clobber=True)


def main():

    # PARSE OPTIONS ###########################################################

    desc = "Convert PNG or JPEG files to FITS images"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("filearg", nargs=1, metavar="FILE",
                        help="the FITS file to convert")
    args = parser.parse_args()
    input_file_path = args.filearg[0]

    output_file_path = os.path.splitext(input_file_path)[0] + ".fits"

    # READ AND SAVE DATA ######################################################

    image_array = load_image(input_file_path) # image_array is a 2D numpy array
    save_fits_file(image_array, output_file_path)


if __name__ == "__main__":
    main()
