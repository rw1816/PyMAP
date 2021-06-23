# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 21:35:17 2020

@author: rw1816

"""
import h5py
import numpy as np
import scipy.signal as signal
from scipy.ndimage import gaussian_filter
from scipy.optimize import curve_fit
from fastpeakfind import sub_pixel
import image_proc
import h5py

def filter_position(time, x_pos, y_pos, config):
    
    dt = time[1] - time[0]
    Fs = 1/dt
    
    fpass=config['laserdata']['pass_freq'][0][0]
    fstop=config['laserdata']['stop_freq'][0][0]
    ripple=config['laserdata']['max_ripple'][0][0]
    
    atten = abs(20*np.log10(ripple))    #max ripple in dB 
    nq=0.5*Fs #nyquist frequency
    #assume width of transition region = fstop
    w=fstop/nq
    #ratio of cutoff frequency to sampling frequency. Determined this empirically
    #from the matlab script. Could be dodgy
    cutoff=fstop/Fs
    
    num_taps, beta = signal.kaiserord(atten, w)
    taps = signal.firwin(num_taps, cutoff, window=('kaiser', beta),
              scale=False, fs=Fs)
    
    x_pos_f = signal.filtfilt(taps, 1, x_pos)
    y_pos_f = signal.filtfilt(taps, 1, y_pos)
    
    return x_pos_f, y_pos_f
    
def process_laser_data(pico_data, cam1raw, cam2raw, cih_info, config, end_frame):
    
    time=pico_data['time']
    x_raw=pico_data['x_raw']
    y_raw=pico_data['y_raw']
    diode=pico_data['diode']
    
    x_pos_f, y_pos_f = filter_position(time, x_raw, y_raw, config)
    
    vdt = 1/cih_info['Record Rate(fps)']
    
    frame_time = np.arange(0, end_frame)*vdt
    frame_time = np.round(frame_time, 9)
    
    #Linearly interpolate to get positions at video frame times
    x_frame_pos = np.interp(frame_time, time, x_pos_f)
    y_frame_pos = np.interp(frame_time, time, y_pos_f)
    
    # Similarly, interpolate laser pulse data to get values at video frame times
    lpulse = np.interp(frame_time, time, diode)
    
    return x_frame_pos, y_frame_pos, lpulse, frame_time

# def set_end_frames(end_frame, cih_info, cam1raw, pico_data):
    
#     if end_frame=[-1]:
        
#         cam_frames=cih_info['Total Frames']
#         pico_frames=len(pico_data)
        
#         if 

def findspotfits(pico_data, cam1raw, cam2raw, end_frame, cih_info, config_path, memory_chunk_size):
    
    config=h5py.File(config_path, 'r') #load in the config file (still a matfile)
    
    #do processing on the pico data
    x_frame_pos, y_frame_pos, lpulse, frame_time = process_laser_data(pico_data, cam1raw, cam2raw, cih_info, config, end_frame)
    
    ##now process cam data and align the two
    intervals=raw_blocker(memory_chunk_size, end_frame)
    cam1_peaks = np.zeros((2,end_frame));
    cam2_peaks = np.zeros((2,end_frame))
    
    for block_start,block_end in zip(intervals[:-1], intervals[1:]):
        
        
        #read in frames from raw data for each camera
        cam1proc=cam1raw[:,:,block_start:block_end]
        cam2proc=cam1raw[:,:,block_start:block_end]
        
        # rotate camera images
        cam1proc=image_proc.rotate_camera_images(cam1raw[:,:,block_start:block_end], 1)
        cam2proc=image_proc.rotate_camera_images(cam2raw[:,:,block_start:block_end], 2)
        
        # Remove background noise (for images when laser is off (no spot))
        # finds all pixels below and estimated noise value and sets to 0
        cam1proc[cam1proc < config['imagedata']['estimated_noise_cam1'][0][0]] = 0
        cam2proc[cam2proc < config['imagedata']['estimated_noise_cam2'][0][0]] = 0
    
        # Calculate threshold params for peak finder function
        block_length=block_end-block_start
        for i in range(0, block_length-1):
            
            cur_frame=block_start+i
            thresh=np.array([cam1proc[:,:,i].max(axis=0).min(), cam1proc[:,:,i].max(axis=1).min()]).max()

            #   find some peaks for cam 1
            peaks = sub_pixel(cam1proc[:,:,i],thresh)
            # Check to see if peaks were found
            # Obtain peak in terms of pixel value (not real size)
            if np.size(peaks) != 0:
                cam1_peaks[:,cur_frame] = peaks[0:1] # Save only coords of first found peak
                
            else:
                cam1_peaks[:,cur_frame] = np.array([np.nan,np.nan]) # When no peak found list NaN for coords
            
            # Repeat above but for other camera
            thresh=np.array([cam2proc[:,:,i].max(axis=0).min(), cam2proc[:,:,i].max(axis=1).min()]).max()

            #   find some peaks for cam 1
            peaks = sub_pixel(cam1proc[:,:,i],thresh)
            # Check to see if peaks were found
            # Obtain peak in terms of pixel value (not real size)
            if np.size(peaks) != 0:
                cam2_peaks[:,cur_frame] = peaks[0:1] # Save only coords of first found peak
                
            else:
                cam2_peaks[:,cur_frame] = np.array([np.nan,np.nan]) # When no peak found list NaN for coords
            
    laser_on=lpulse > 0.1
    
    idxfit1 = np.isfinite(cam1_peaks[1,:])*laser_on
    idxfit2 = np.isfinite(cam2_peaks[1,:])*laser_on
    
    cam1_xfit=findoffsetfit(x_frame_pos[idxfit1],y_frame_pos[idxfit1],cam1_peaks[1,idxfit1],'cam1_xfit', end_frame)
    cam1_yfit=findoffsetfit(x_frame_pos[idxfit1],y_frame_pos[idxfit1],cam1_peaks[2,idxfit1],'cam1_yfit', end_frame)
    cam2_xfit=findoffsetfit(x_frame_pos[idxfit2],y_frame_pos[idxfit2],cam2_peaks[1,idxfit2],'cam2_xfit', end_frame)
    cam2_yfit=findoffsetfit(x_frame_pos[idxfit2],y_frame_pos[idxfit2],cam2_peaks[2,idxfit2],'cam2_yfit', end_frame)

def raw_blocker(memory_chunk_size, end_frame):
    rem=end_frame % memory_chunk_size
    if rem==0:
        intervals=np.zeros(end_frame//memory_chunk_size +1)
    else:
        intervals=np.zeros(end_frame//memory_chunk_size +2)
    intervals[:-1]=np.arange(1, end_frame-1, memory_chunk_size)-1
    intervals[-1]=end_frame-1
    
    return intervals.astype('uint16')
    
def findoffsetfit(x_data, y_data, z_data, fitname, end_frame):    
    
    xy_data=np.c[x_data, y_data]
    scipy

    
    
    
    
    
    