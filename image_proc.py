# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 13:53:27 2020

@author: rw1816
"""
import numpy as np
from skimage.transform import rotate

def rotate_camera_images(I, cameraNum):
    
   # If it is first camera, just rotate then vert flip to align image XY with scanhead XY
   #rotation seems to be 22 degrees
   for i in range(0, I.shape[2]):
    if cameraNum == 1:
       I = np.flipud(rotate(I, -22, order=1, resize=False, preserve_range=True, clip=False)).astype('uint16')
       
   #% If it is second camera, flip the image horizontally (extra mirror) then rotate and vert flip
    elif cameraNum == 2:
        I = np.flipud(rotate(np.fliplr(I), -22, order=1, resize=False, preserve_range=True)).astype('uint16')

    return I