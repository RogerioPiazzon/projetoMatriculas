import gdown

def downloadparams(path):
    gdown.download_folder(url="https://drive.google.com/drive/folders/1SLJw0eK5ZgHoQ9Z4c5InMsQY1TfWlSmP?usp=drive_link", 
                      output=f"{path}\docs",
                      quiet=True)