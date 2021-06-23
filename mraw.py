# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 17:15:18 2020

https://github.com/ladisk/pyMRAW/

@author: rw1816
"""
from os import path
import numpy as np

def get_cih(filename):
    
    SUPPORTED_FILE_FORMATS = ['mraw', 'tiff']
    SUPPORTED_EFFECTIVE_BIT_SIDE = ['lower', 'higher']
    
    name, ext = path.splitext(filename)
    if ext == '.cih':
        cih = dict()
        # read the cif header
        with open(filename, 'r') as f:
            for line in f:
                if line == '\n': #end of cif header
                    break
                line_sp = line.replace('\n', '').split(' : ')
                if len(line_sp) == 2:
                    key, value = line_sp
                    try:
                        if '.' in value:
                            value = float(value)
                        else:
                            value = int(value)
                        cih[key] = value
                    except:
                        cih[key] = value
                        
    else:
        
        raise Exception('Unsupported configuration file ({:s})!'.format(ext))

    # check exceptions
    bits = cih['Color Bit']
    if bits < 12:
        print('Not 12bit ({:g} bits)! clipped values?'.format(bits))
                # - may cause overflow')
                # 12-bit values are spaced over the 16bit resolution - in case of photron filming at 12bit
                # this can be meanded by dividing images with //16
                
    ebs = cih['EffectiveBit Side']
    if ebs.lower() not in SUPPORTED_EFFECTIVE_BIT_SIDE:
        raise Exception('Unexpected EffectiveBit Side: {:g}'.format(ebs))
        
    if (cih['File Format'].lower() == 'mraw') & (cih['Color Bit'] not in [8, 16]):
        raise Exception('pyMRAW only works for 8-bit and 16-bit files!')
        
    if cih['Original Total Frame'] > cih['Total Frame']:
        print('Clipped footage! (Total frame: {}, Original total frame: {})'.format(cih['Total Frame'], cih['Original Total Frame'] ))

    return cih


def load_images(mraw_file, cih_obj, N, roll_axis=True):
    """
    loads the next N images from the binary mraw file into a numpy array.
    Inputs:
        mraw: an opened binary .mraw file
        h: image height
        w: image width
        N: number of sequential images to be loaded
        roll_axis (bool): whether to roll the first axis of the output 
            to the back or not. Defaults to True
    Outputs:
        images: array of shape (h, w, N) if `roll_axis` is True, or (N, h, w) otherwise.
    """
    h = cih_obj['Image Height']
    w = cih_obj['Image Width']
    bit = cih_obj['Color Bit']
    
    if int(bit) == 16:
        bit_dtype = np.uint16
    elif int(bit) == 8:
        bit_dtype = np.uint8
    else:
        raise Exception('Only 16-bit and 8-bit files supported!')

    images = np.memmap(mraw_file, dtype=bit_dtype, mode='r', shape=(N, h, w))
    
    if roll_axis:   #omitting true implies true
        return np.rollaxis(images, 0, 3)
    else:
        return images
