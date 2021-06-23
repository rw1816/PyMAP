# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 15:10:43 2020
Melt Pool Analysis programme
translated to Python by RJW
@author: rw1816
"""
#-------------------------
#CONTROL VARIABLES
#%Convert raw data to raw data matfile (call convertrawdata())
load_mrawdata = True
#Generate new spotfits matfile (call findspotfits())
new_spotfits = True
#Process data & create new results matfile (call preprocdata())
new_results = True
#OPTIONAL - Generate metrics about raw camera images as part of the results
save_rawcamerametrics = False

#Plot metric vs frame number graphs
do_frameplots = 0
#Plot metric vs time graphs
do_timeplots = 0

#specify end frame number when generating new matfiles (i.e. to truncate)
raw_end_frame = 220000
spotfits_end_frame = 220000
results_end_frame = 220000


#specify config matfile to use
configfn = 'config_matfile.mat'

#--------------------------------------------------------------------------
#specify image folder - DON'T FORGET TRAILING \  --------------------------
imgfoldername = 'G:\PD_monitoring_data\build1_220920\L903\'

#specify picoscope data file to use--------------------------------------------
laserdatafilename = 'L903.mat'

laserdatafn = imgfoldername + laserdatafilename
#--------------------------------------------------------------------------
#Specify matfile filenames to use

#specify raw data matfile to save to / use, save in imagefolder
rawmatfilename = 'rawdataALLFRAMES.mat'
rawmatfilefn = imgfoldername + rawmatfilename

#specify spot fit matfile to save to / use, save in imagefolder
spotfitfilename = 'spotfitsALLFRAMES.mat'
spotfitfn = imgfoldername + spotfitfilename

#specify results matfile to save to / use, save in imagefolder
resultsfilename = 'resultsALLFRAMES.mat'
resultsfn = imgfoldername + resultsfilename

#--------------------------------------------------------------------------
#Carry out the main processing:

#get raw data from original raw files and convert to matfile:
if (load_mrawdata == True):
    loadrawdata(rawmatfilefn, imgfoldername, laserdatafn, raw_end_frame)s

if (new_spotfits == True):
    #findspotfitsand save
    findspotfits(spotfitfn, rawmatfilefn, spotfits_end_frame, configfn)

if (new_results == True):
    # Do preprocessing and save to matfile
    preprocdata(resultsfn, rawmatfilefn, spotfitfn, results_end_frame, save_rawcamerametrics, configfn)

#--------------------------------------------------------------------------
#Plot Simple Graphs:

if do_timeplots == True:
   plotmetricgraphs_time(resultsfn)

if do_frameplots == True:
   plotmetricgraphs_frame(resultsfn)