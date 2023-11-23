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
from unidecode import unidecode
from utils import utils_module
from PIL import Image
import pathlib

class Ocr():
    tika_client = TikaApp(file_jar=f"{pathlib.Path(__file__).parent.resolve()}\\tika-app-1.20.jar")

    def average(self,
                lst):
        return round(sum(lst) / len(lst),2)

    def classifier(self,
                   pdf_file):
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

            if len(res_img) == 0 and len(res_text) == 0:
                return "erro"
            elif len(res_img) == 0:
                return "doc"
            elif len(res_text) == 0:
                return "image"
            elif self.average(res_img) > self.average(res_text):
                # print("Documento composto de {}% de imagens".format(self.average(res_img)*100))
                return "image"
            else:
                # print("Documento composto de {}% de textos".format(self.average(res_text)*100))
                return "doc"

    def img_to_text (self,filename):

        img_clean = cv2.imread(filename)
        img_clean = Image.open(filename)
        text = pytesseract.image_to_string(img_clean,lang='por')

        return unidecode(text)

    def img_file(self,IMG_FILE_PATH):
        path,file = os.path.split(os.path.abspath(IMG_FILE_PATH))
        output = path + "/converted_files/"+file.replace(".pdf", ".txt")

        utils_module.create_folder(path + "/converted_files/")

        text_final = self.img_to_text(IMG_FILE_PATH)
        arq = open(output, "w")
        arq.write(text_final)
        arq.close()
        return output

    def convert_pdf_pytesseract(self,
                                PDF_FILE_PATH):
        try:
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
                text_final += self.img_to_text(filename)
                os.remove(filename)

            path,file = os.path.split(os.path.abspath(PDF_FILE_PATH))
            output = path + "/converted_files/"+file.replace(".pdf", ".txt")
            utils_module.create_folder(path + "/converted_files/")

            arq = open(output, "w")
            arq.write(text_final)
            arq.close()
            return output
        except Exception as error:
            print("Erro: ",error)
            return None


    def convert_Tika(self,
                     PDF_FILE_PATH):
        try:
            text = self.tika_client.extract_only_content(PDF_FILE_PATH.replace("\\", "/"))
            path,file = os.path.split(os.path.abspath(PDF_FILE_PATH))
            output = path + "/converted_files/"+file.replace(".pdf", ".txt")

            utils_module.create_folder(path + "/converted_files/")
            arq = open(output, "w")
            arq.write(text)
            arq.close()
            return output
        except Exception as error:
            print("Erro: ",error)
            return None


    def pdf_file(self,
                 path):
        tipo = self.classifier(path)
        if tipo:
            return self.convert_pdf_pytesseract(path)
        elif tipo == "doc":
            return self.convert_Tika(path)
        else:
            print(f"Nao foi possivel converter o documento {path}")
            return None 

ocr_module = Ocr()