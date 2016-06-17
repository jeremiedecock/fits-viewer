#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Documentation: http://docs.astropy.org/en/stable/io/fits/index.html

import argparse
from astropy.io import fits
import os

import PIL.Image as pil_img # PIL.Image is a module not a class...
import numpy as np


def load_fits_file(input_file_path):
    # Open the FITS file
    hdu_list = fits.open(input_file_path)

    image_array_list = []

    for hdu in hdu_list:
        if hdu.is_image:
            image_array = hdu.data   # "hdu.data" is a Numpy Array

            if image_array.ndim == 2:

                # If there are only one image (image_array is an 2D array)
                image_array_list.append(image_array)

            elif image_array.ndim == 3: # TODO

                # If there is more than one image (image_array is an 3D array)
                for image_sub_array in image_array:
                    image_array_list.append(image_sub_array)

            elif image_array.ndim == 4: # TODO

                # If there is more than one image (image_array is an 3D array)
                for image_sub_array in image_array:
                    for image_sub_sub_array in image_sub_array:
                        image_array_list.append(image_sub_sub_array)

    # Close the FITS file
    hdu_list.close()

    return image_array_list


def save_to_png(image_array, output_file_path, min_val=None, max_val=None):
    """
    image_array is the image and it should be a 2D numpy array with values in the range [0,255].
    min_val and max_val are normalization parameters (the minimum and maximum value of a pixel).
    """

    if image_array.ndim != 2:
        raise Exception("The input image should be a 2D numpy array.")

    mode = "L"                           # "L" = grayscale mode
    pil_image = pil_img.new(mode, (image_array.shape[1], image_array.shape[0]))

    # FLIP THE IMAGE IN THE UP/DOWN DIRECTION #############
    # WARNING: with fits, the (0,0) point is at the BOTTOM left corner
    #          whereas with pillow, the (0,0) point is at the TOP left corner
    #          thus the image should be converted

    image_array = np.flipud(image_array)

    # Normalize values ################
    # (FITS pixels value are unbounded but PNG pixels value are in range [0,255])
    if min_val is None:
        min_val = image_array.min()
    if max_val is None:
        max_val = image_array.max()

    image_array = image_array.astype(np.float64)
    image_array -= min_val
    image_array /= (max_val - min_val)
    image_array *= 255.
    image_array = image_array.astype(np.uint8)

    # Save ############################
    # WARNING: nested list and 2D numpy arrays are silently rejected!!!
    #          data *must* be a list or a 1D numpy array!
    pil_image.putdata(image_array.flatten())
    pil_image.save(output_file_path)


def main():

    # PARSE OPTIONS ###########################################################

    parser = argparse.ArgumentParser(description="Convert FITS files to PNG images")
    parser.add_argument("filearg", nargs=1, metavar="FILE", help="the FITS file to convert")
    args = parser.parse_args()
    input_file_path = args.filearg[0]

    output_file_path_prefix = os.path.splitext(input_file_path)[0]

    # READ AND SAVE DATA ######################################################

    image_array_list = load_fits_file(input_file_path)

    if len(image_array_list) > 1:
        for image_index, image_array in enumerate(image_array_list):
            save_to_png(image_array, "{}_{}.png".format(output_file_path_prefix, image_index))
    else:
        save_to_png(image_array_list[0], "{}.png".format(output_file_path_prefix))


if __name__ == "__main__":
    main()
