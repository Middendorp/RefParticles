#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from sys import platform
from io import BytesIO
from skimage import io, exposure, transform
import os
import warnings



def get_header_data(dir_stub):
    """fetch the header info from 'Stub Summary.txt' """

    filename = os.path.join(dir_stub,'Stub Summary.txt')

    # open the stub invo .csv file
    with open(filename,'r') as f:
        file_inputdata = f.read()

    # extract the header-info from inp_data (first 14 lines)
    inp_header = file_inputdata.splitlines()[0:14]

    # Date

    # Acc.Voltage
    voltage = float(inp_header[4].split(',')[2])

    # Magnification
    magnification = float(inp_header[5].split(',')[1])

    # Measurement Time
    MeasTime = float(inp_header[10].split(',')[2])

def get_stubinfo(file_stub):
    """read the file input stream and store in pandas Dataframe"""
    
    # open the stub invo .csv file
    with open(file_stub,'r') as f:
        file_inputdata = f.read()


    # extract the PA data
    # gets the data from the .csv file generated from EDAX PA searc
    #
    # for python 3 the io needs to be handled correctly
    #
    # The csv files has \r newlines, which np.genfromtxt cannot handle (bug ?)
    #
    # The stream is opened as text io (universal newline mode) which converts the newlines to \n
    #
    # inp_data is rewritten into a in memory bytestream for np.genfromtxt
    # comments is set to "//" to overide the default value "#" (fixes problems reading names)
    import_stub = np.genfromtxt(BytesIO(file_inputdata.encode()), 
                            delimiter=",", skip_header = 14, 
                            names = True, autostrip=True, comments='//')


    return pd.DataFrame(import_stub)

def crop_img(image, center_x, center_y, size_x, size_y):
    """crops an image given the center of the cropped image and the width and height"""

    # The coordinates from the stub info has (0,0) in the bottom left
    # whereas skimage uses top left as origin
    # transformation using size of img
    imgsize_x = image.shape[1]
    imgsize_y = image.shape[0]
    
    center_y = imgsize_y - center_y
    
    y_down = center_y - int(np.abs(size_y/2))
    y_up = center_y + int(np.abs(size_y/2))
    x_down = center_x - int(np.abs(size_x/2))
    x_up = center_x + int(np.abs(size_x/2))
    
    # the window to be cropped should be within bounds of the image
    if x_down < 0:           # shift to positive x
            shift = np.abs(x_down)
            x_down += shift
            x_up += shift

    elif x_up > imgsize_x:   # shift to negative x
            shift = x_up - imgsize_x
            x_down -= shift
            x_up -= shift       
    
    if y_down < 0:             # shift to positive y
            shift = np.abs(y_down)
            y_down += shift
            y_up += shift
            
    elif y_up > imgsize_y:     # shift to negative y    
            shift = y_up - imgsize_y
            y_down -= shift
            y_up -= shift            
            
    rescaled_cropped_img = transform.rescale(
        image[y_down:y_up, x_down:x_up],
        3,
        order = 0
    )
    # exposure.rescale_intensity(cropped_img, out_range='uint8')

    #return the cropped image and resclaed image
    return rescaled_cropped_img

def process_fields(df_stub, dir_stub, ext):
    """ Process the fields and create cropped images

        df_stub:    Pandas Dataframe object containing the stub info

        dir_stub:   path object for the directory containing the fields

        ext:        String containing the extension
    """

    # if cropped files are present, ask if user really wants to reprocess

    # Create list of images to be loaded and cropped from stub data
    fields = df_stub.Field
    img_list = [dir_stub + '/fld'+'{:0>4d}'.format(int(field_no))+'/search' + ext for field_no in fields]
    coll = io.ImageCollection(img_list)

    # Loop over fields
    for field_no, field in enumerate(fields):
        # fetch the image from the ic
        img = coll[field_no]

        # fetch the index of particles on the field
        particles = df_stub[df_stub.loc[:,'Field']==field].Part.values

        # Loop over particles
        for particle_no, particle in enumerate(particles):
            x_c, y_c = df_stub.loc[df_stub.loc[:,'Part']==particle,['X_cent','Y_cent']].values.flatten()
            x_size, y_size = df_stub.loc[df_stub.loc[:,'Part']==particle,['X_width','Y_height']].values.flatten()

            # crop image from collection
            cropped_img = crop_img(img, int(x_c), int(y_c), int(x_size), int(y_size))
        
            # save in '/cropped/part0000.png'
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                io.imsave(dir_stub + 
                          '/cropped/' + 
                          '{:0>4d}'.format(int(field))+
                          '{:0>4d}'.format(int(particle_no)+1) +
                          ext, cropped_img
                          )

def walk_stubdir(path):
    """Walks the stub directory and extracts the locations.
    
    Keyword arguments:
    path -- the path searched for stub PA data 
    

    returns dictionary with PA data locations as a list
    """

    # find the pa search directory
    # stub_dir  - stub directories
    # stub_info - .csv info files
    stub_dir = []
    stub_info = []
    extension = []

    for root, dirs, files in os.walk(wdir):
        if 'Stub Summary.txt' in files:

            # Found directory with Stub Summary
            stub_dir.append(root)
            print(files)

            # Check is subdirectory 'cropped' exists, unless create
            if 'cropped' not in dirs:
                os.makedirs(os.path.join(root,'cropped'))

            # Look for the .csv files containing the stub info
            for file in files:
                if file.endswith('.csv'):
                    stub_info.append(os.path.join(root, file))

    # Extract the extension of the image
    for root, dirs, files in os.walk(os.path.join(stub_dir[0],'fld0001')):
        if 'search.png' in files:
            extension.append('.png')

        elif 'search.bmp' in files:
            extension.append('.bmp')
        
        elif 'search.tif' in files:
            extension.append('.tif')
    datalocation = dict([('stub_dir',stub_dir),('stub_info',stub_info),('extension',extension)])
    return datalocation

if platform == 'win32':
    root_dir = 'C:/Users/ma.duerr/sciebo/Reference Particle Production/ParticleBrowser/'

elif platform == 'darwin':
    root_dir = '/Users/mduerr/sciebo/Reference Particle Production/ParticleBrowser/'

# Preparations for processing of stub info

# Directory containing the stub data
directory = 'SG170216_06'

# Create the full path
wdir = os.path.join(root_dir,directory)

# Retrieve the PA data locations
if os.path.exists(wdir):
    data_loc = walk_stubdir(wdir)
else:
    print('PA directory not found')

# Retrieve the stub_info
df = get_stubinfo(data_loc['stub_info'][0])

# Process the images
process_fields(df, data_loc['stub_dir'][0], data_loc['extension'][0])
