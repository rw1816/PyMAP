# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 14:43:44 2021

@author: rw1816
"""
from skimage.measure import label, regionprops
from scipy.signal import medfilt2d, convolve2d
import numpy as np
import cv2

def sub_pixel(I, thres):
    
    if I.any():     #i.e. if image is non-zero
    
        I=medfilt2d(I.astype('float32')).astype('uint16')
        
        _,I=cv2.threshold(I, thres, 1, cv2.THRESH_TOZERO)
        
        if I.any():   #if the image is still non zero
        
            # smooth image
            filt=matlab_gauss2D((7,7),1)
            I=convolve2d(I,filt,'same')
        
            # Apply again threshold (and change if needed according to SNR)
            _,I=cv2.threshold(I, thres*0.9, 1, cv2.THRESH_TOZERO)
            
            label_img = label(I.astype('bool'), connectivity=2)
            stats = regionprops(label_img, intensity_image=I)
            area_list=[stat.area for stat in stats]
            area_list = area_list <= np.mean(area_list)+2*np.std(area_list)
            cents=np.array([stat.weighted_centroid for stat in stats])[area_list==True]
            
        else:
           cents=[]    
    else:
        cents=[]
    return cents        
            
            
def matlab_gauss2D(shape=(7,7),sigma=1):
    """
    2D gaussian mask - should give the same result as MATLAB's
    fspecial('gaussian',[shape],[sigma])
    """
    m,n = [(ss-1.)/2. for ss in shape]
    y,x = np.ogrid[-m:m+1,-n:n+1]
    h = np.exp( -(x*x + y*y) / (2.*sigma*sigma) )
    h[ h < np.finfo(h.dtype).eps*h.max() ] = 0
    sumh = h.sum()
    if sumh != 0:
        h /= sumh 

    return h
        