# -*- coding: utf-8 -*-
__author__ = 'kharada'

### HDFWriter(h5py)

import glob
import h5py
import scipy.stats as stats
import scipy.signal as signal
import scipy.io
import numpy as np

### Load data from Mat

brainData = []
brainDescriptions = []
movementData  = []
movementDescriptions  = []
eventTime  = []
eventData  = []
eventDescriptions  = []
eyeTrackData  = []
eyeTrackDescriptions  = []
dataMatrix = []

title = '20100803S1_SCT_K2_ToruYanagawa_mat_ECoG128-Eye9-Motion22-Event3'
directory = title + '/'
expTime = '2010/08/03'
monkey = 'Kuma10mks'
positionOrder = ['Left shoulder of monkey with ECoG','Left elbow of monkey with ECoG','Left wrist of monkey with ECoG','Right wrist of monkey with ECoG','Right elbow of monkey with ECoG','Right wrist of monkey with ECoG','Front and left side of head of monkey with ECoG','Right and right side of head of monkey with ECoG','Back and left side of head of monkey with ECoG','Back and right side of head of monkey with ECoG','Left side of head of experimenter','Left shoulder of experimenter','Left hand of experimenter','Right side of head of experimenter','Right shoulder of experimenter','Right hand of experimenter','Left shoulder of opponent monkey','Left elbow of opponent monkey','Left wrist of opponent monkey','Right shoulder of opponent monkey','Right elbow of opponent monkey','Right wrist of opponent monkey']
eyeTrackOrder = ['IGNORE-Index','IGNORE-Undefined','Angle of x-axis (deg)','Angle of y-axis (deg)','Speed of eye movement','Gaze time','Pupil size (X)','Pupil size (Y)','Eye blink']
eventDesc = 'start_Low:1, end_Low:2, start_LowNC:3, end_LowNC:4, start_High:5, end_High:6, start_HighNC:7, end_HighNC:8, start_rest:9, end_rest:10'

for dataFile in glob.glob(directory + "ECoG_ch*.mat"):
    ch = dataFile.split('_ch')[1].split('.mat')[0]
    if ch.startswith('0'):
        ch = ch.split('0')[1]
    
    matData = scipy.io.loadmat(dataFile) 
    chData = matData.get('ECoGData_ch'+ch)[0]
    
    brainData.append(chData)
    description = "ECoGData_ch" + ch
    brainDescriptions.append(description)
    
timeFile = glob.glob(directory + "ECoG_time.mat")[0]
matData = scipy.io.loadmat(timeFile)
timeData = matData.get('ECoGTime')[0]
brainDataTimeOffset = timeData[0]
    
motionFile = glob.glob(directory + "Motion.mat")[0]
matData = scipy.io.loadmat(motionFile)
timeData = matData['MotionTime'][0]
movementTimeOffset = timeData[0]

xyzOrder = ['X','Y','Z']

for motionIndex in range(len(matData['MotionData'])):
    oneMotionData = matData['MotionData'][motionIndex]
    xyzData = oneMotionData[0].T
    for xyzIndex in range(len(xyzData)):
        movementData.append(xyzData[xyzIndex])
        description = "Motion :  " + positionOrder[motionIndex] + "-" + xyzOrder[xyzIndex]
        movementDescriptions.append(description)
    
eyeFile = glob.glob(directory + "EyeTrack.mat")[0]
# print eyeFile
matData = scipy.io.loadmat(eyeFile)
timeData = matData['EyeTrackTime'][0]
eyeTrackTimeOffset = timeData[0]


data = matData['EyeTrackData'].T
for dataIndex in range(len(data)):
    if dataIndex <=1:
        continue
    oneEyeData = data[dataIndex]
    eyeTrackData.append(oneEyeData)
    description = "EyeTrack :  " + eyeTrackOrder[dataIndex]
    eyeTrackDescriptions.append(description)

eventFile = glob.glob(directory + "Event.mat")[0]
# print eventFile
matData = scipy.io.loadmat(eventFile)
eventTimeData = matData['EventTime']
eventData = matData['EventData']
description = "Experiment Event :  " + eventDesc
eventDescriptions.append(description)


## Write data to HDF5

# Define output file.
outputFilename = title + '.h5'

# Write to the file.
with h5py.File(outputFilename, 'w') as f: #write an HDF5 file

    # File header
    # title,schema,...
    fileHeaderGroup=f.create_group("fileHeader") # /fileHeader
    fileHeaderGroup.create_dataset('title',data='Neurotycho Social Competition Task')
    fileHeaderGroup.create_dataset('schema',data=['default:http://brainliner.jp/1.0']) # default schema, so namespacing is not required # this is an array, so multiple schemata are allowed
    fileHeaderGroup.create_dataset('schemaDef',data=['UC'])
    fileHeaderGroup.create_dataset('date',data=expTime)
    fileHeaderGroup.create_dataset('description',data="There were two monkeys sitting around a table. ECoG data and eye tracking data were recorded from one monkey. Motion data were captured from both monkeys and experimenter. For each trial, one food reward was placed on the table. If one monkey was dominant to the other, he could take the reward withouthesitation. But, if he was submissive, he could not take the reward because of social suppression. ECoG data were obtained from one monkey under different hierarchycal conditions by pairing with multiple monkeys.")
    fileHeaderGroup.create_dataset('url',data='http://brainliner.jp/data/brainliner-admin/Social_Competition_Task')
    fileHeaderGroup.create_dataset('pubmedId',data=20407639)
    fileHeaderGroup.create_dataset('affiliation',data="Naotaka Fujii, RIKEN")
    fileHeaderGroup.create_dataset('license',data="Public Domain Dedication and License (PDDL)")
    # Subject
    fileHeaderGroup.create_dataset('subjectLabel',data="monkey " + monkey)
    fileHeaderGroup.create_dataset('subjectSpecies',data="monkey")

    # Data contents(HDF-Groups)
    # Groups for behavioral data
    behaviorGroup=f.create_group("group1") # /group1
    behaviorGroup.create_dataset("data", data=movementData,compression="gzip")
    propGroup1 = behaviorGroup.create_group("props")
    propGroup1.create_dataset('title',data='Motion Sensor markers')
    propGroup1.create_dataset('description',data='MotionData: MotionData is a time x marker matrix containing 3-D position of marker')
    propGroup1.create_dataset('type',data='movement')
    propGroup1.create_dataset('dataUnits',data='mm')
    propGroup1.create_dataset('dataNames',data=movementDescriptions)
    propGroup1.create_dataset('samplingRate',data=120) #Hz
    propGroup1.create_dataset('startTime',data=movementTimeOffset) #offset in s from file start

    # Data contents(HDF-Groups)
    # Groups for brain activity data
    brainGroup=f.create_group("group2") # /group2
    brainGroup.create_dataset("data",data=brainData,compression="gzip")
    propGroup2 = brainGroup.create_group("props")
    propGroup2.create_dataset('title',data='ECoG 64 channels')
    propGroup2.create_dataset('description',data='ECoGData_chN: ECoG signal (μV) recorded from electrodeN (1‐32), sampled at 1kHZ. The Location of electrode is documented in "B.png".')
    propGroup2.create_dataset('type',data='ECoG')
    propGroup2.create_dataset('dataUnits',data='micro volt')
    propGroup2.create_dataset('dataNames',data=brainDescriptions)
    propGroup2.create_dataset('samplingRate',data=1000) #Hz
    propGroup2.create_dataset('startTime',data=brainDataTimeOffset) #offset in s from file start

    # Data contents(HDF-Groups)
    # Groups for eye tracking data
    eyeGroup=f.create_group("group3") # /group3
    eyeGroup.create_dataset("data", data=eyeTrackData,compression="gzip")
    propGroup3 = eyeGroup.create_group("props")
    propGroup3.create_dataset('title',data='Eye Tracking Data')
    propGroup3.create_dataset('description',data='EyeTrackData: EyeTrackData is a time x variable matrix containing various variable describing eye motion.')
    propGroup3.create_dataset('type',data='movement')
    propGroup3.create_dataset('dataNames',data=eyeTrackDescriptions)
    propGroup3.create_dataset('samplingRate',data=120) #Hz
    propGroup3.create_dataset('startTime',data=eyeTrackTimeOffset) #offset in s from file start

    # Data contents(HDF-Groups)
    # Groups for event data
    eventGroup=f.create_group("group4") # /group4
    eventGroup.create_dataset("data", data=eventData,compression="gzip")
    eventGroup.create_dataset("timestamps", data=eventTimeData,compression="gzip")
    propGroup4 = eventGroup.create_group("props")
    propGroup4.create_dataset('title',data='Event Data(Task Design)')
    propGroup4.create_dataset('description',data='EventData: EventData is a one row-vector contains event id.')
    propGroup4.create_dataset('type',data='stimulus')
    propGroup4.create_dataset('typeDescription',data=eventDesc)
    propGroup4.create_dataset('dataNames',data=eventDescriptions)

