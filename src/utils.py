import os
from PyPDF2 import PdfReader
import gdown

class UtilsMatricula():

    def create_folder(self,namefolder):
        if not os.path.exists(namefolder):
            os.makedirs(namefolder)

    def check_pdf(self,fullfile):
        with open(fullfile, 'rb') as f:
            try:
                pdf = PdfReader(f)
                info = pdf.metadata
                if info:
                    return True
                else:
                    return False
            except Exception as e:
                return False

    def download_params(self,path):
        gdown.download_folder(url="https://drive.google.com/drive/folders/1SLJw0eK5ZgHoQ9Z4c5InMsQY1TfWlSmP?usp=drive_link", 
                        output=f"{path}\docs",
                        quiet=True)

utils_module = UtilsMatricula()