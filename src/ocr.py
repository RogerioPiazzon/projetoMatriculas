"""MÓDULO PARA PROCESSAMENTO DOS ARQUIVOS PDF EM TXT"""
import glob
import numpy as np
import pytesseract
import sys
import cv2
import fitz
import os

from tikapp import TikaApp
from pdf2image import convert_from_path

# print(f"{os.path.dirname(sys.argv[0])}\\tika-app-1.20.jar")

tika_client = TikaApp(file_jar=f"{os.path.dirname(sys.argv[0])}\\tika-app-1.20.jar")

def Average(lst):
    return round(sum(lst) / len(lst),2)

def classifier(pdf_file):
    with open(pdf_file,"rb") as f:
        pdf = fitz.open(f)
        res_img = []
        res_text = []
        for page in pdf:
            total_page_area = abs(page.rect)
            image_area = 0.0
            text_area = 0.0
            for b in page.get_text("blocks"):
                if '<image:' in b[4]:
                    r = fitz.Rect(b[:4])
                    image_area = image_area + abs(r)
                else:
                    r = fitz.Rect(b[:4])
                    text_area = text_area + abs(r)
            
            res_img.append(image_area/total_page_area)
            res_text.append(text_area/total_page_area)

        if Average(res_img) > Average(res_text):
            print("Documento composto de {}% de imagens".format(Average(res_img)*100))
            return True
        else:
            print("Documento composto de {}% de textos".format(Average(res_text)*100))
            return False
        
def convert_pdf_pytesseract(PDF_FILE_PATH):
    pages = convert_from_path(PDF_FILE_PATH)
    image_counter = 1
    for page in pages:
        filename = (
            PDF_FILE_PATH.replace(".pdf", "") + "_page_" + str(image_counter) + ".jpg"
        )
        page.save(filename, "JPEG")
        image_counter += 1
    filelimit = image_counter - 1
    text_final = ""
    for i in range(1, filelimit + 1):
        filename = PDF_FILE_PATH.replace(".pdf", "") + "_page_" + str(i) + ".jpg"
        img_clean = cv2.imread(filename)
        text = pytesseract.image_to_string(img_clean)
        text = text.replace("-\n", "")
        text_final += text
    arq = open(PDF_FILE_PATH.replace(".pdf", ".txt"), "w")
    arq.write(text_final)
    arq.close()


def convert_Tika(PDF_FILE_PATH):
    text = tika_client.extract_only_content(PDF_FILE_PATH.replace("\\", "/"))
    arq = open(PDF_FILE_PATH.replace(".pdf", ".txt"), "w")
    arq.write(text)
    arq.close()


def transformFile(path):
    print(f"Convertendo {path}")
    if classifier(path):
        convert_pdf_pytesseract(path)
    else:
        convert_Tika(path)