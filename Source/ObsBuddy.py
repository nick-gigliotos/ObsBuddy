#Just prints something when recording starts (must be enabled obviously)

#LOTS OF GLOBALS. I do not think I can pass parameters to these functions so the globals
#are neseccary atm. I will test this later.

#Obs module, Python will say it cant find it but if its ran in OBS it will work
import obspython as obs
import time
import math
import io
import os

#Global for debug messages
DEBUG_MODE = False

#Global for whether the script is enabled because the obs call for that is long
isEnabled = False

#Global to help tell when OBS has stopped recording
isRecording = False

#Globals for keeping track of times
startTime = 0

splitStartTime  = 0

#Minimum split time (seconds)?
MIN_SPLIT_TIME = 2

#Global for how many splits
splitCounter = 0

#LFSLKFNDSLKFNSLKFNSLKFN OBS SUCKS AND REGISTERS KEY UP AND KEY DOWN AS SEPERATE HOTKEY
#EVENTS. SO I NEED AN OFFEST TIMER TO PREVENT A SPLIT STARTING RIGHT AFTER A SPLIT ENDS
#FROM THE KEY UP. THIS MEANS IT IS IMPOSSIBLE TO START A SPLIT 3 SECONDS AFTER ENDING ONE.
OFFSET = 3
offsetTimer = 0

#OBS function, loads script. Sets enabled to false on load.
def script_load(settings):
    if (DEBUG_MODE): 
        print("Calling Load")

    obs.obs_data_set_bool(settings, "enabled", False)
    obs.obs_data_set_bool(settings, "debugMode", False)
    obs.obs_hotkey_register_frontend("splitHotkey", "Split Hotkey", handleSplits)

#Creats the enabled property when the script is instanited
def script_properties():
    if (DEBUG_MODE): 
        print("Calling properties")	
        
    props = obs.obs_properties_create()
    obs.obs_properties_add_bool(props, "enabled", "Enabled")
    obs.obs_properties_add_path(props, "filePath", "File Path", obs.OBS_PATH_DIRECTORY, None, None)
    obs.obs_properties_add_bool(props, "debugMode", "Debug Mode")
    
    return props

#This script is ran when a property is changed inside the OBS UI.
#Updates variables based on the property changes.
def script_update(settings):
    global isEnabled
    global DEBUG_MODE

    if (DEBUG_MODE): 
        print("Calling Update")
        print("isEnabled:", isEnabled)

    #Update value of enabled
    isEnabled = obs.obs_data_get_bool(settings, "enabled")
    DEBUG_MODE = obs.obs_data_get_bool(settings, "debugMode")

    #Add or remove functions based on whether the script is enabled
    if(isEnabled):
        obs.timer_add(onRecordingStart, 1000)
        obs.timer_add(onRecordingEnd, 100)
    else:
        obs.timer_remove(onRecordingStart)
        obs.timer_remove(onRecordingEnd)

#If OBS is recording and this script is Enabled. Print Something.
def onRecordingStart():
    global isRecording
    global startTime
    global splitCounter
    
    if(isEnabled and obs.obs_frontend_recording_active() and not isRecording):
        if DEBUG_MODE:
            print("Timer Start")
        isRecording = True
        splitCounter = 0
        startTime = math.floor(time.time())
        

def onRecordingEnd():
    global isRecording
    global startTime

    if(isEnabled and not obs.obs_frontend_recording_active() and isRecording):
        if DEBUG_MODE:
            print("Timer End")
        isRecording = False

def handleSplits(isPressed):
    global startTime
    global splitStartTime
    global isRecording
    global splitCounter
    global offsetTimer

    if(isRecording and isEnabled and math.floor(time.time()) - offsetTimer > OFFSET):
        if(splitStartTime == 0):
            if DEBUG_MODE:
                print("Split started")
            splitStartTime = math.floor(time.time())
            offsetTimer = 0
        else:
            endTime =  math.floor(time.time()) - splitStartTime
            if(endTime > MIN_SPLIT_TIME):
                if DEBUG_MODE:
                    print("Split ended")
                splitCounter += 1
                saveTimes(splitStartTime - startTime, endTime)
                splitStartTime = 0
                offsetTimer = math.floor(time.time())
            


#CONFUSING VARIABLE NAMES. FIX??
def saveTimes(startTime, endTime):
    global splitCounter

    currentDirectory = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    savePath = os.path.relpath('..\\Splits\\splits.txt', os.path.dirname(__file__))
    file = io.open(savePath, "a+")
    file.write("Split" + str(splitCounter) + ": Start time-" + str(startTime) + " End time-" + str(endTime) + "\n")
    file.close()
    os.chdir(currentDirectory)


