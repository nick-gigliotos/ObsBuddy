##OBS Buddy Settings
import os
import json

class Settings():
    def __init__(self):
        self.settings_path = os.path.dirname(os.path.realpath(__file__))+'\\settings.json'
        self.data = self.get_settings()
        
    def get_settings(self):
        '''Returns the settings data from the Settings.json file'''
        with open(self.settings_path,'r+') as file:
            return json.load(file)


    def update_settings(self,values):
        '''Iterates through the settings data to update the data based upon
        new values from the user
        '''
        for k1 in self.data:
            for k2 in self.data[k1]:
                for x in values:
                    if k2 == x:
                        self.data[k1][k2] = values.get(x)

        with open(self.settings_path, 'w+') as file:
            json.dump(self.data, file, indent=4)
                    
        return self.data
            
