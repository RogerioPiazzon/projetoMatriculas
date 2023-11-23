import os,sys,logging,time,pathlib
from PyPDF2 import PdfReader
import gdown

class UtilsMatricula():
    logger = object

    def __init__(self):
        self.__create_log()


    def __create_log(self):
        now = time.strftime("%d%m%Y%H%M%S")
        folder_log = os.path.join(pathlib.Path(__file__).parent.resolve().parent.resolve(),'log')
        log_output = os.path.join(folder_log,f"log_{now}.log")
        self.create_folder(folder_log)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(formatter)

        file_handler = logging.FileHandler(filename=log_output,mode="a")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(stdout_handler)


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
            
    def log(self,msg,type='INFO'):
        if type == 'INFO':
            self.logger.info(msg)
        elif type == 'ERROR':
            self.logger.error(msg)
        elif type == 'DEBUG':
            self.logger.debug(msg)
        elif type == 'WARN':
            self.logger.warn(msg)
        else:
            self.logger.critical(msg)

    def download_params(self,path):
        gdown.download_folder(url="https://drive.google.com/drive/folders/1SLJw0eK5ZgHoQ9Z4c5InMsQY1TfWlSmP?usp=drive_link", 
                        output=f"{path}\docs",
                        quiet=True)

utils_module = UtilsMatricula()