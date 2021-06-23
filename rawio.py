# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 17:05:29 2020

Replaces the first section (of 3) of the old code, convertrawdata.m.
There's no need to loop through all that binary unpacking 12 bits. 
Save as 16bit out of Photron and we can access this architecture easily and 
efficiently using memory mapped arrays. 


Calls on slightly modified versions of the functions in pyMRAW (see mraw.py)
Loads in:
    
- cih_info as a dictionary object 
- Camera 1 & 2 raw gray images as memory mapped numpy arrays

No point in saving this info out in any other format

@author: rw1816
"""
import mraw
import numpy as np
import os
import pandas as pd

def load_rawdata(foldername, usr_end_frame):
        
    nargs = len(locals())
    cih_path = os.path.join(foldername, 'C001H001S0001.cih')
    cam1_path = os.path.join(foldername, 'C001H001S0001.mraw')
    cam2_path = os.path.join(foldername, 'C002H001S0001.mraw')
    
    # we only need to read one .cih
    cih_info = mraw.get_cih(cih_path)
    
    if usr_end_frame == -1:
        num_frames = cih_info['Total Frame']
        
    elif nargs < 2:
        num_frames = cih_info['Total Frame']
    
    elif nargs == 2 and usr_end_frame < cih_info['Total Frame']:
        num_frames = usr_end_frame
    
    else:
        raise Exception('Number of frames unclear')
        
    print("Loading {0} frames".format(num_frames))
    
    cam1_raw = mraw.load_images(cam1_path, cih_info, num_frames, roll_axis=True)
    cam2_raw = mraw.load_images(cam2_path, cih_info, num_frames, roll_axis=True)
    
    return cam1_raw, cam2_raw, cih_info
