import os

class UtilsMatricula():
    
    def create_folder(self,namefolder):
        if not os.path.exists(namefolder):
            os.makedirs(namefolder)

utils_module = UtilsMatricula()