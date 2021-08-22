#Just prints something when recording starts (must be enabled obviously)

#LOTS OF GLOBALS. I do not think I can pass parameters to these functions so the globals
#are neseccary atm. I will test this later.

#Obs module, Python will say it cant find it but if its ran in OBS it will work
import obspython as obs
import time
import datetime
import math
import io
import os
import shutil
import Settings

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
rewindOffsetTimer = 0

#OBS names the video based on the time started, so this saves the time the video has started
#at in the format OBS uses to name a video. THIS IS DIFFERENT THEN startTime. startTime is
#to tell how long a video has been running. Incase the name if off by one second, I will
#store the name plus 1 second as well and try that if the original fails.
videoNameTimes = []

#Gotta Store dem hotkeys globally
hotkeys = {}


#OBS function, loads script. Sets enabled to false on load.
def script_load(settings):
    if (DEBUG_MODE): 
        print("Calling Load")
        print("github sucks")

    obs.obs_data_set_bool(settings, "enabled", False)
    obs.obs_data_set_bool(settings, "debugMode", False)
    hotkeys["splitHotkey"] = obs.obs_hotkey_register_frontend("splitHotkey", "Split Hotkey", handle_splits)
    hotkeySaveArray = obs.obs_data_get_array(settings, "splitHotkey")
    obs.obs_hotkey_load(hotkeys["splitHotkey"], hotkeySaveArray)
    obs.obs_data_array_release(hotkeySaveArray)
    hotkeys["rewindHotkey"] = obs.obs_hotkey_register_frontend("rewindHotkey", "Rewind Hotkey", rewind)
    hotkeySaveArray = obs.obs_data_get_array(settings, "rewindHotkey")
    obs.obs_hotkey_load(hotkeys["rewindHotkey"], hotkeySaveArray)
    obs.obs_data_array_release(hotkeySaveArray)

def script_save(settings):
    global hotkeys
    
    obs.obs_data_set_array(settings, "splitHotkey", obs.obs_hotkey_save(hotkeys["splitHotkey"]))
    obs.obs_data_set_array(settings, "rewindHotkey", obs.obs_hotkey_save(hotkeys["rewindHotkey"]))    

#Creats the enabled property when the script is instanited
def script_properties():
    if (DEBUG_MODE): 
        print("Calling properties")	
        
    props = obs.obs_properties_create()
    obs.obs_properties_add_bool(props, "enabled", "Enabled")
    obs.obs_properties_add_bool(props, "debugMode", "Debug Mode")
    
    return props

#This script is ran when a property is changed inside the OBS UI.
#Updates variables based on the property changes.
def script_update(settings):
    global isEnabled
    global DEBUG_MODE

    #Update value of enabled
    isEnabled = obs.obs_data_get_bool(settings, "enabled")
    DEBUG_MODE = obs.obs_data_get_bool(settings, "debugMode")

    if (DEBUG_MODE): 
        print("Calling Update")
        print("isEnabled:", isEnabled)

    #Add or remove functions based on whether the script is enabled
    if(isEnabled):
        obs.timer_add(on_recording_start, 1000)
        obs.timer_add(on_recording_end, 100)
    else:
        obs.timer_remove(on_recording_start)
        obs.timer_remove(on_recording_end)

#If OBS is recording and this script is Enabled. Print Something.
def on_recording_start():
    global isRecording
    global startTime
    global splitCounter
    
    
    
    if(isEnabled and obs.obs_frontend_recording_active() and not isRecording):
        getVideoName()
        if DEBUG_MODE:
            print("Timer Start")
        isRecording = True
        splitCounter = 0
        startTime = math.floor(time.time())
        

def on_recording_end():
    global isRecording
    global startTime

    if(isEnabled and not obs.obs_frontend_recording_active() and isRecording):
        if DEBUG_MODE:
            print("Timer End")
        isRecording = False
        moveVideo()

def handle_splits(isPressed):
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
                save_times(splitStartTime - startTime, splitStartTime - startTime + endTime)
                splitStartTime = 0
                offsetTimer = math.floor(time.time())
            



def save_times(beginTime, endTime):
    global splitCounter
    global videoNameTimes

    startTime = format_time(beginTime)
    endTime = format_time(endTime)
    currentDirectory = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    savePath = Settings.Settings().get_settings().get("output").get("video_path") + videoNameTimes[0] + "/" + "splits.txt"
    file = io.open(savePath, "a+")
    file.write("Split" + str(splitCounter) + ": " + startTime + ":" + endTime + "\n")
    file.close()
    os.chdir(currentDirectory)

def format_time(timeToFormat):
    hours = timeToFormat//3600
    timeToFormat -= hours * 3600
    minutes  = timeToFormat//60
    timeToFormat -= minutes * 60

    hoursTensDigit = ""
    minutesTensDigit = ""
    secondsTensDigit = ""

    if(hours < 10):
        hoursTensDigit = "0"
    if(minutes < 10):
        minutesTensDigit = "0"
    if(timeToFormat < 10):
        secondsTensDigit = "0"

    formattedTime = hoursTensDigit + str(hours) + ":" + minutesTensDigit + str(minutes) + ":" + secondsTensDigit +  str(timeToFormat)
    return formattedTime

def rewind(isPressed):
    global startTime
    global splitCounter
    global rewindOffsetTimer

    if(DEBUG_MODE):
        print("Rewind ran")

    rewindTime = int(Settings.get_settings().get("split").get("rewind_seconds"))
    currentTime = math.floor(time.time()) - startTime
    beginTime = 0
    if(currentTime > rewindTime):
        beginTime = currentTime - rewindTime

    if(math.floor(time.time()) - rewindOffsetTimer > OFFSET):
        splitCounter += 1
        save_times(beginTime, currentTime)
        rewindOffsetTimer = math.floor(time.time())

def getVideoName():
    global videoNameTimes

    name = Settings.Settings().get_settings().get("output").get("video_title")
    if(name == "default"):
        videoNameTimes.append(datetime.datetime.now())
        videoNameTimes.append(datetime.datetime.now() - datetime.timedelta(seconds=1))
        for i in range(2):
            year = videoNameTimes[i].year
            month = videoNameTimes[i].month
            if(month < 10):
                month = "0" + str(month)
            day = videoNameTimes[i].day
            if(day < 10):
                day = "0" + str(day)
            hour = videoNameTimes[i].hour
            if(hour < 10):
                hour = "0" + str(hour)
            minute = videoNameTimes[i].minute
            if(minute < 10):
                minute = "0" + str(minute)
            second = videoNameTimes[i].second
            if(second < 10):
                second = "0" + str(second)
            videoNameTimes[i] = str(year) + "-" + str(month) + "-" + str(day) + " " + str(hour) + "-" + str(minute) + "-" + str(second)
    
    if(os.path.exists(Settings.Settings().get_settings().get("output").get("obs_save_path") + "/" + videoNameTimes[1] +".mp4")):
        videoNameTimes[0] = videoNameTimes[1]
        videoNameTimes.pop()

    os.mkdir(Settings.Settings().get_settings().get("output").get("video_path") + videoNameTimes[0])

    if(DEBUG_MODE):
        print(str(i), videoNameTimes[0])
    
            


        
            
def moveVideo():
    global videoNameTimes

    source = Settings.Settings().get_settings().get("output").get("obs_save_path") + "/" + videoNameTimes[0] +".mp4"
    destination = Settings.Settings().get_settings().get("output").get("video_path") + videoNameTimes[0] + "/"

    try:
        shutil.move(source, destination)
        if(DEBUG_MODE):
            print("Video Name:", videoNameTimes[0], "moved to location:", destination)
    except:
            print("No file with that name found. Video will be located in the OBS directory it was saved in.")
            videoNameTimes.clear()


    videoNameTimes.clear()
        



