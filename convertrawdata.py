# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 15:29:04 2020

@author: rw1816
"""
import os
#import mraw

def convertrawdata(matfilefn, imgfoldername, laserdatafn, end_frame):

    #read in imagedata from a companion .cih file
    imagedata = loadimagedata(imgfoldername);
    
    #save imagedata as well
    #m.imagedata = imagedata;

    #convert camera data and save it in the matfile
    #mraw2npy(m, imagedata, end_frame)
    
   #read in laser data and save it
    #m.laserdata = loadlaserdata(laserdatafn, end_frame, imagedata.FrameRate)

    #save end frame, useful info
    imagedata['end_frame'] = end_frame
    
    return imagedata

#%%
def loadimagedata(imgfoldername):

    imageData = readcih(imgfoldername)
    imageData["folderName"] = imgfoldername
    
    #Specify the precision used to initialise the image array
    precision_check_array = [2^3, 2^4, 2^5, 2^6]
    for val in precision_check_array:
        if val != precision_check_array[3]:
            if imageData["ColorBit"] <= val:
                imageData["ArrayInitPrecision"] = 'uint' + str(val)
                break

        elif val == precision_check_array[3]:
            
            imageData["ArrayInitPrecision"] = 'double'
            break

    imageData["Precision"] = '*ubit'+ str(imageData["ColorBit"])
    
    bits_per_pixel = imageData["ColorBit"]
    bits_per_byte = 8
    imageData["NBytesPerFrame"] = imageData["Pixels"] * bits_per_pixel / bits_per_byte

    imageData['CurrFrame'] = 1

    return imageData


#%%
def readcih(folderName):
    
    imageData=dict()
    
    fileName=os.path.join(folderName, 'C001H001S0001.cih')
    headerCount = 0
    
    with open(fileName, 'r') as f:
        
        lines = f.readlines()
    
        for line in lines:
            
                if "Total Frame" in line:
                    imageData["Total_Frames"] = int(line.split(':')[1])
                    headerCount = headerCount+1
    
                if "Image Width" in line:
                    imageData["Width"] = int(line.split(':')[1])
                    headerCount = headerCount+1
    
                if "Image Height" in line:
                    imageData["Height"] = int(line.split(':')[1])
                    headerCount = headerCount+1
    
                if "Record rate(fps) " in line:
                    imageData["FrameRate"] = int(line.split(':')[1])
                    headerCount = headerCount+1
    
                if "Color Bit " in line:
                    imageData["ColorBit"] = int(line.split(':')[1])
                    headerCount = headerCount+1
                
            # If header count reaches 5, break the loop
                if headerCount == 5:
                    break
    
    imageData["Header"] = str(lines)
    imageData["Pixels"] = imageData["Width"] * imageData["Height"]

    return imageData

