#Just prints something when recording starts (must be enabled obviously)

#Obs module, Python will say it cant find it but if its ran in OBS it will work
import obspython as obs

#Test for commits

#Global for debug messages
DEBUG_MODE = True

#Global for whether the script is enabled because the obs call for that is long
ENABLED = False

#OBS function, loads script. Sets enabled to false on load.
def script_load(settings):
    if (DEBUG_MODE): 
        print("Calling Load")
        
    obs.obs_data_set_bool(settings, "enabled", False)

#Creats the enabled property when the script is instanited
def script_properties():
    if (DEBUG_MODE): 
        print("Calling properties")	
        
    props = obs.obs_properties_create()
    obs.obs_properties_add_bool(props, "enabled", "Enabled")
    
    return props

#This script is ran when a property is changed inside the OBS UI.
#Updates variables based on the property changes.
def script_update(settings):
    if (DEBUG_MODE): 
        print("Calling Update")

    #Update value of enabled
    ENABLED = obs.obs_data_get_bool(settings, "enabled")

    #Add or remove functions based on whether the script is enabled
    if(ENABLED):
        obs.timer_add(OnRecordingStart, 1000)
    else:
        obs.timer_remove(OnRecordingStart)

#If OBS is recording and this script is Enabled. Print Something.
def OnRecordingStart():
    if(DEBUG_MODE):
        print("It ran")
    if(ENABLED and obs. obs_frontend_recording_active()):
        print("Subsribe to ZardyZ")
        
