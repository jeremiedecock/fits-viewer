# TODO

## common

- [ ] Write docstrings
- [ ] Write documentation
- [ ] Ask to add fitsviewer to the NASA list of FITS Image Viewer

## fitsviewer

- [x] Set the window title
- [x] Add an "open" button to open files from the GUI
- [x] Show the colorbar (from GUI and from command line)
- [x] Choose the colormap (from GUI and from command line)
- [x] Show an histogram (from GUI and from command line)
- [x] Memorize the last opened directory
- [x] Menu "File/Open Resent"
- [x] Choose the HDU to display (checkbuttons in the menu bar: HDU / ...)
- [ ] Small improvements:
    - [ ] "Recent File List": if the file is not available anymore then display a message "File not found" and remove the file from the "Recent File List"
    - [ ] "Select File Dialog": when the "cancel" button is clicked the function return the '' (empty) string which cause an exception... Change that to silently ignore empty return strings...
    - [ ] Fix the issue with the wrong number of "bins" when making the histrogram
    - [ ] "HDU" menu: use a radio button to indicate which HDU is currently used
    - [ ] Add a Makefile to clean the working directory, publish the current version on PyPI, install from PyPI, update, ...
- [ ] Manage 3D pictures (...)
- [ ] Manage 4D (and above) pictures ?
- [ ] Display HDU header (use the TTK Notebook widget to choose between displaying the image or the header array (with ttk.treeview))
- [ ] Choose scale (linear, log, ...) (from GUI and from command line)
- [ ] Show statistics (resolution, mean, std, ...)
- [ ] Save the figure to PNG/PDF/... (from GUI and from command line)
- [ ] Manage 2D tables (...)
- [ ] Split gui: backend (matplotlib draw) + frontend (tk + nox)
- [ ] Add a command: fitsviewer-nox which uses the nox frontend (for shell scripts)
- [ ] Let the user indicates the min/max values for normalization of images (colormap + colorbar)
- [ ] Show level lines (from GUI and from command line)
- [ ] Zoom
- [ ] Show bargraph for the current row/line (like in DS9)
- [ ] How to display hexagonal pictures from HESS/CTA (and keep the software generic) ?
- [ ] Error dialogs for Tk frontend
- [ ] "Help/About..." dialogs for Tk frontend

## png2fits

- [x] Use the input file basename as the default output file path
- [ ] Set the output file path
- [ ] Set the min/max value of the output domain
- [ ] Ask before removing the output file + add a --force option
- [ ] Convert multiple files
- [ ] Convert multiple PNG files to one 3D FITS file

## fits2png

- [x] Use the input file basename as the default output file path
- [x] Convert one 3D FITS file to multiple PNG files
- [ ] Set the min/max value of the input domain
- [ ] Ask before removing the output file + add a --force option
- [ ] Set the output file path
- [ ] Convert multiple files

## fits2gif

- [ ] Convert one 3D FITS file to one animated GIF file

## fitsinfo

- [ ] Returns the fits header in stdout
