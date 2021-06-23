# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 17:58:53 2020

@author: rw1816
"""
import h5py
import pandas as pd
import numpy as np
import scipy.signal as signal
from scipy.io import loadmat
import os
 
def import_matfile(filename, startrow, endrow):

    """
    Time, Diode, Trig, Sync, x_pos, y_pos, Len
    """
    
    f = loadmat(filename)
        
    #unpack the matfile
    Diode = f['A'][startrow:endrow]
    y_pos = f['B'][startrow:endrow]
    x_pos = f['C'][startrow:endrow]
    t_start = f['Tstart']
    t_interval = f['Tinterval']
    pico_length = f['Length']
        
    #generate time vector
    t = np.arange(t_start, t_start+(t_interval*pico_length), t_interval)
    t = np.round(t, decimals=9)
    
    startrow=int(startrow)
    endrow=int(endrow)
    
    #if sample rate is higher that 1MHz, downsample data to speed up program
    
    if t_interval < 1e-6:
        
        t, Diode, y_pos, x_pos = downsample_pico(t, Diode, y_pos, x_pos, t_interval, startrow, endrow)
        
        print('Downsampling pico data')
    
    del(f)
    t=t[startrow:endrow]
    
    return t, Diode, x_pos, y_pos, pico_length

def load_picodata(foldername, pico_name, end_frame, cih_info):
    
    filename = os.path.join(foldername, pico_name)
    
    time, _, _, _, pico_length = import_matfile(filename, 2, 4)
    pico_time_diff = time[1]-time[0]
    
    cam_time_diff = 1 / cih_info['Record Rate(fps)']
    
    multiplier = cam_time_diff / pico_time_diff

    #trigger time (time = 0s) may not be at row 2, so need to figure out start
    #row
    startrow = int((0 - time[0])/ pico_time_diff+1)

    # Obtain end row
    if end_frame == -1:
        end_frame=cih_info['Total Frame']
    else:
        end_frame=end_frame
    endrow = int(startrow + (end_frame - 1) * multiplier)
    
    #RJW use this bodge to just load in all of the laser data needed when you have more camera footage than pico
    #data
    if endrow > pico_length:
        endrow = -1 
        print("** WARNING: There is less pico data than cam data **")
    
    #declare a dataframe for the pico data
    pico_data = pd.DataFrame(index=np.arange(0, endrow-startrow), columns=['time', 'diode', 'x_raw', 'y_raw']) 
    
    pico_data['time'], pico_data['diode'], pico_data['x_raw'], pico_data['y_raw'], pico_length = import_matfile(filename, startrow, endrow)
#    t,d,x,y,l=import_matfile(filename, startrow, endrow)
    return pico_data
    
def downsample_pico(t, Diode, y_pos, x_pos, Tinterval, startrow, endrow):
    
    # this is a bit of a bodge, will this cause issues???
    ds_ratio = np.floor(1e-6/Tinterval)
    t = signal.decimate(t, ds_ratio)
    Diode = signal.decimate(Diode, ds_ratio)
    y_pos = signal.decimate(y_pos, ds_ratio)
    x_pos = signal.decimate(x_pos, ds_ratio)
    
def set_end_frames(end_frame, cih_info, cam1raw, pico_data):
    
     if end_frame== -1:
         
         end_frame_cam=cih_info['Total Frames']
         end_frame_pico=len(pico_data)
        
         if end_frame_pico > end_frame_cam:
             
             print('Truncating pico data (normal operation')
             
         elif end_frame_cam > end_frame_pico:
             
             print('Truncating cam frames *WARNING*')
             
         else: 
             
             raise "why are there equal numbers of cam and pico frames"
             
     else: #i.e. if a frame range is specified
    
        end_frame_cam=end_frame
        
