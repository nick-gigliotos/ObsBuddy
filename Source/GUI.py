import PySimpleGUI as sg

## Was built at work and couldn't test
## Will implement OBSBuddy support ASAP
#import ObsBuddy

import time

## Obs Theme (Need to put into function)
obs_theme ={ "BACKGROUND": "#3a393a",
                "TEXT": "WHITE",
                "INPUT": "#464546",
                "SCROLL": "#4c4c4c",
                "TEXT_INPUT": "#c9c7c1",
                "BUTTON": ("#c9c7c1", "#4c4c4c"),
                "PROGRESS": sg.DEFAULT_PROGRESS_BAR_COLOR,
                "BORDER": 1,
                "SLIDER_DEPTH": 0,
                "PROGRESS_DEPTH": 0
                }

## Generic Functions
def format_time(raw_time):
    '''Returns the given time in format HH:MM:SS'''
    return '{:02d}:{:02d}.{:02d}'.format((raw_time // 100) // 60, (raw_time // 100) % 60, raw_time % 100)

## Popups

def split_popup():
    '''Shows after user is done recording if setting is enabled'''
    check = sg.popup_yes_no('Would you like to split the video now?',title='Split?')
    return check
    
## Layouts
sg.theme_add_new('OBS',obs_theme)
sg.theme('OBS')

no_pad = ((0,0),(0,0))

## First screen the user sees. Contains the timer and access to all other screens
def get_main_layout():
    '''Generates the "Main Screen" allowing the user to:
    1. Start Recording
    2. Split Videos
    3. View Settings
    4. Exit Program
    '''
    global no_pad

    timer_buttons = [[sg.Button('Start Split',key='split_status',size=(15,1)),sg.Button('Create Rewind Split',key='rewind_split',size=(15,1))]]

    timer_layout = [[sg.Text('',size=(8,1),font=('Comic Sans',20),key='timer',text_color='green')],
                    [sg.Text('',size=(20,1),font=('Comic Sans', 14),key='split_text')],
                    [sg.Column(timer_buttons,key='timer_buttons')]]
    
    main_layout = [[sg.Frame(None, timer_layout, element_justification='c', border_width=0)],
                   [sg.Button('Start Recording',key='rec_status',size=(15,1),pad=no_pad)],
                   [sg.Button('Split Video',key='split_video',size=(15,1),pad=no_pad)],
                   [sg.Button('Settings',key='settings',size=(15,1),pad=no_pad)],
                   [sg.Button('Exit',key='exit',size=(15,1),pad=no_pad)]]
    
    return main_layout

## Contains all the settings for the program. Split into mulitple frames.
## Setting sections include:
## General
## Splits
## Output
def get_settings_layout():
    '''Layout that contains all settings including:
    1. General
    2. Splits
    3. Output
    '''
    #global settings_data
    
    header_pad = ((5,5),(1,1))
    settings_sections = [[sg.Button('General',key='general_s',size=(15,1),pad=header_pad)],
                     [sg.Button('Split Settings',key='split_s',size=(15,1),pad=header_pad)],
                     [sg.Button('Output',key='output_s',size=(15,1),pad=header_pad)]]

    general_frame = [[sg.Text('General')],
                     [sg.Checkbox('Disable Split Popup after recording',default=True,key='split_popup')]]

    split_frame =  [[sg.Text('Split Settings')],
                    [sg.Text('Start/End Split'),sg.Input(key='split_hotkey',default_text='s')],
                    [sg.Text('Create "Rewind" Split'), sg.Input(key='rewind_hotkey',default_text='r')],
                    [sg.Text('Seconds to "Rewind"'), sg.Input(key='rewind_seconds',default_text='60')]]


    output_frame = [[sg.Text('Output Settings')],
                    [sg.Text('Default Project Name:'),sg.Input(key='project_name',default_text='Insert Cool Video Name Here')],
                    [sg.Text('Default Project Location:'),sg.Input(key='project_path',default_text='Subscribe to Zardy Z'),sg.FileBrowse()]]
                    

    settings_layout = [[sg.Text('Settings',font=('Times New Roman', 30))],
                       [sg.Column(settings_sections,background_color='#1f1e1f'),
                        sg.Frame(None,general_frame,key='general_frame',visible=True),
                        sg.Frame(None,split_frame,key='split_frame',visible=False),
                        sg.Frame(None,output_frame,key='output_frame',visible=False)],
                       [sg.Button('Ok',key='settings_ok'),sg.Button('Cancel',key='settings_cancel'),sg.Button('Apply',key='settings_apply')]]

    return settings_layout


## Contains everything related to splitting a recording.
def get_splitting_layout():
    '''WIP. Will allow user to select video path
    and splits path to split video'''
    splitting_layout = [[sg.Text('Splitting',font=('Times New Roman', 30))],
                        [sg.Text('Video File:'),sg.Input(key='file_to_split'),sg.FileBrowse()],
                        [sg.Text('Splits File:'), sg.Input(key='splits_file'),sg.FileBrowse()],
                        [sg.Button('Cancel',key='splitting_cancel'),sg.Button('Proceed',key='splitting_apply')]]
    
    return splitting_layout


## Combines all layouts into one universal layout via frames
def get_combined_layout():
    '''Combines the main_layout,settings_layout, and splitting_layout'''
    layout = [[sg.Image(filename='rsz_obs_icon.png',pad=no_pad),sg.Text('BS Buddy V.1',font=('Times New Roman', 40),pad=no_pad)],
              [sg.Frame(None,layout=get_main_layout(),key='main_frame',element_justification='c', border_width=0,visible=True),
               sg.Frame(None,layout=get_settings_layout(),key='settings_frame',element_justification='c', border_width=0,visible=False),
               sg.Frame(None,layout=get_splitting_layout(),key='splitting_frame',element_justification='c', border_width=0,visible=False)]]
    return sg.Window('OBS Buddy', layout, element_justification = 'c', finalize=True)



## Window Related Functions
def change_rec_button(window):
    '''Checks the text of the recording button and updating the main window accordingly'''
    if window['rec_status'].get_text() == 'Start Recording':
        #keyboard.on_press_key("s", lambda _:create_split(window,current_time))
        window.FindElement('rec_status').Update(text='Stop Recording')
        window.FindElement('timer').Update(text_color='red')
        starting_time = int(round(time.time()*100))
        window.FindElement('settings').Update(disabled=True)
        window.FindElement('split_video').Update(disabled=True)
        window['timer_buttons'].unhide_row()
        return True, starting_time
    elif window['rec_status'].get_text() == 'Stop Recording':
        window.FindElement('rec_status').Update(text='Start Recording')
        window.FindElement('timer').Update(text_color='green')
        window.FindElement('settings').Update(disabled=False)
        window.FindElement('split_video').Update(disabled=False)
        window['timer_buttons'].hide_row()
        return False, split_popup()

def change_split_button(window):
    '''Updates the split button and displays text.
    Returns True for split_status and the current split time
    '''
    if window['split_status'].get_text() == 'Start Split':
        window.FindElement('split_status').Update(text='Stop Split',disabled=True)
        window.FindElement('timer').Update(text_color='blue')
        window.FindElement('split_text').Update(value='Split Started at: '+str(format_time(int(round(time.time()*100)) - starting_time)),text_color='blue')
        return True, int(round(time.time()*100))
    elif window['split_status'].get_text() == 'Stop Split':
        window.FindElement('split_status').Update(text='Start Split')
        window.FindElement('timer').Update(text_color='red')
        window.FindElement('split_text').Update(value='Split Ended at: '+str(format_time(int(round(time.time()*100)) - starting_time)),text_color='red')
        return False, int(round(time.time()*100))

def rewind_button(window):
    '''Updates the rewind button and displays text
    Returns True for rewind_status and the current rewind split time
    '''
    window.FindElement('rewind_split').Update(disabled=True)
    window.FindElement('timer').Update(text_color='purple')
    window.FindElement('split_text').Update(value='Split Created at: '+str(format_time(int(round(time.time()*100)) - 180 - starting_time)),text_color='purple')
    return True, int(round(time.time()*100))
    

def update_frames(visual_states,window):
    '''Updates the visual state of window frames'''
    for k,v in visual_states.items():
        window.FindElement(k).Update(visible=v)

window = get_combined_layout()
rec_status = False
split_status = False
rewind_status = False
current_time = 0
last_split_time = 0
window['timer_buttons'].hide_row()
## Main event loop
while True:
    #print(rec_status)
    event,values = window.read(timeout=10)
    #if global isRecording == True:
        #rec_status = True
    if rec_status == True:
        current_time = int(round(time.time()*100)) - starting_time
        if rewind_status == True:
            if int(round(time.time()*100))-last_rsplit_time >= 300:
                window.FindElement('split_status').Update(disabled=False)
                window.FindElement('rewind_split').Update(disabled=False)
                window.FindElement('split_text').Update(value='')
                if split_status == True:
                    window.FindElement('timer').Update(text_color='blue')
                else:
                    window.FindElement('timer').Update(text_color='red')
                rewind_status = False
        elif split_status == True:
            if int(round(time.time()*100))-last_split_time >= 300:
                window.FindElement('split_status').Update(disabled=False)
                window.FindElement('rewind_split').Update(disabled=False)
                window.FindElement('split_text').Update(value='')
                
        else:
            if int(round(time.time()*100))-last_split_time >= 300:
                window.FindElement('split_text').Update(value='')

    if event == 'exit' or event == None:
        window.close()
        break
    elif event == 'rec_status':
        rec_status, starting_time = change_rec_button(window)
        if starting_time == 'Yes':
            window['split_video'].click()
            
    elif event == 'split_status':
        split_status, last_split_time = change_split_button(window)
        print(last_split_time)

    elif event == 'rewind_split':
        rewind_status, last_rsplit_time = rewind_button(window)
        

    ## Setting related events
    elif event == 'settings':
        update_frames({'main_frame':False,'settings_frame':True,'splitting_frame':False},window)
    elif event == 'general_s':
        update_frames({'general_frame':True,'split_frame':False,'output_frame':False},window)
    elif event == 'split_s':
        update_frames({'general_frame':False,'split_frame':True,'output_frame':False},window)
    elif event == 'output_s':
        update_frames({'general_frame':False,'split_frame':False,'output_frame':True},window)
    elif event == 'settings_ok' or event =='settings_apply':
        print(values)
        update_frames({'main_frame':True,'settings_frame':False,'splitting_frame':False},window)
    elif event == 'settings_cancel':
        # Don't save Settings to text document
        update_frames({'main_frame':True,'settings_frame':False,'splitting_frame':False},window)

    ## Splitting Related Events   
    elif event == 'split_video':
        update_frames({'main_frame':False,'settings_frame':False,'splitting_frame':True},window)
    elif event == 'splitting_cancel':
        update_frames({'main_frame':True,'settings_frame':False,'splitting_frame':False},window)
            
    


    window.FindElement('timer').update(value='{:02d}:{:02d}.{:02d}'.format((current_time // 100) // 60, (current_time // 100) % 60, current_time % 100))
        
            
