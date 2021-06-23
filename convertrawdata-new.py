# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 19:36:22 2020

@author: rw1816
"""
import rawio
import pico
import numpy as np
import align

config_path='config_matfile.mat'
foldername="D://OneDrive - Imperial College London//File Transfer//PyMAP//PyMAP//16bit"
piconame='L903.mat'
end_frame=10000
memory_chunk_size = 5000
#use pythonic [-1] for all

cam1raw, cam2raw, cih_info = rawio.load_rawdata(foldername, end_frame)
pico_data = pico.load_picodata(foldername, piconame, end_frame, cih_info)
x_frame_pos, y_frame_pos, laser_on, idxfit1, idxfit2, cam1_peaks, cam2_peaks, end_frame=align.findspotfits(pico_data, cam1raw, cam2raw, end_frame, cih_info, config_path, memory_chunk_size)


print(np.size(cam1raw, 2)/cih_info['Record Rate(fps)'])
print(max(pico_data['time']))





