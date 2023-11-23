"""MÓDULO PARA PROCESSAMENTO DOS DADOS E EXTRAÇÃO DE INFORMAÇÕES"""
import re,os,sys,shutil,pathlib
import pandas as pd
from glob import glob
from datetime import datetime
from ocr import ocr_module
from utils import utils_module

PARENT_PATH = pathlib.Path(__file__).parent.resolve().parent.resolve()

class InfoExtract():
    COLUMNS = ["lower_bound", "upper_bound", "group", "re.I", "multiple", "padrao"]

    def __load_columns_table(
            self,
            name_table: str,
            excel_path: str = f"{PARENT_PATH}/docs/colunas_tabelas.xlsx"):
        """
        Carrega os nomes das variáveis que serão inseridas na tabela respectiva.
        Caso não haja, para o cartório específico um padrão para captura da variável, este método garante o preenchimento com NDA.
        Ele também permite que além do método do cartório específico, sejam utilizados os padrões marcados com a tag 'geral'.
        """
        df = pd.read_excel(excel_path)
        return df["campo"][
            (df["nome_tabela"] == name_table) | ((df["nome_tabela"] == "geral"))
        ].tolist()

    def __load_data_excel(self,
                        excel_path: str):
        "Lê uma tabela de excel simples"
        return pd.read_excel(excel_path)


    def __build_dict(
            self,
            registry,
            excel_path: str = os.path.join(PARENT_PATH,"docs","padroes_informações.xlsx"),
            name_table: str = "informacoes_matriculas"):
        "Carrega os padrões na forma de um dicionário para serem utilizados na extração de informações"
        df_patterns = self.__load_data_excel(excel_path)
        df_name_variables = self.__load_columns_table(name_table)
        df_patterns = df_patterns[df_patterns["cartorio"] == registry]
        if len(df_patterns) == 0 :
            print(f"Padrão não encontrado para o cartorio {registry}")
            print(f"Por favor, verifique o arquivo de padrões em {excel_path}")
            return None
        dic_data = {}
        for row in df_patterns.to_dict("records"):
            dic_data[row["descrição"]] = {k: row[k] for k in self.COLUMNS}
        for k in df_name_variables:
            if k not in dic_data:
                dic_data[k] = "NDA"
        return dic_data

    def __extract_information(
            self,
            registry: str,
            path_files: str):
        """
        registry: nome do cartório cujos padrões serão utilizados, além de padrões com tag 'geral', se existirem
        path_files: caminho absoluto onde os arquivos podem ser encontrados

        Retorna um dataframe que pode ser transformado em um excel ou inserido na base de dados
        """
        if len(registry) == 0:
            registry = "GERAL"
        dict_data = self.__build_dict(registry)
        if dict_data is None:
            return None
        list_files = glob(path_files, recursive=True)
        new_rows = []
        for i,f in enumerate(list_files):
            print("[" + str(i+1)+"/"+str(len(list_files))+"] Analisando", os.path.basename(f))
            text = re.sub(
                r"\s+", " ", " ".join([l for l in open(f, "r", encoding="ISO-8859-1")])
            )
            res = {"arquivo": f, "texto_completo": text}
            for k, dic in dict_data.items():
                text_aux = text[
                    int(dic["lower_bound"] * len(text)) : int(
                        dic["upper_bound"] * len(text)
                    )
                ]
                if dic["re.I"]:
                    if dic["multiple"]:
                        result_search = re.findall(
                            dic["padrao"], text_aux, flags=re.I | re.S
                        )
                    else:
                        result_search = re.search(
                            dic["padrao"], text_aux, flags=re.I | re.S
                        )
                else:
                    if dic["multiple"]:
                        result_search = re.findall(dic["padrao"], text_aux)
                    else:
                        result_search = re.search(dic["padrao"], text_aux)
                if float(dic["multiple"]) == 1.0:
                    res[k] = str(result_search)
                else:
                    res[k] = result_search.group(dic["group"]) if result_search else "NDA"
            new_rows.append(res)
        return pd.DataFrame(new_rows)
    
    def __convert_to_txt(self,filename):
        arq = None
        extension = pathlib.Path(filename).suffix
        if extension.lower() in ['.pdf']:
            if utils_module.check_pdf(filename):
                arq = ocr_module.pdf_file(filename)
        elif extension.lower() in ['.jpeg','.png','.jpg']:
            arq = ocr_module.img_file(filename)
        elif extension.lower() in ['.txt']:
            arq = filename
        else:
            print(f"Formato de arquivo não suportado: {extension}")
        return arq

    def extrair_dados(self,
                      registry: str, 
                      path_files: str):
        
        if os.path.exists(path_files):

            if os.path.isfile(path_files):
                parent,filename = os.path.split(os.path.abspath(path_files))
                print("[1/1] Processando", filename)
                output_path = parent
                utils_module.create_folder(os.path.join(parent,'use_files'))
                file_txt = self.__convert_to_txt(os.path.join(parent,filename))
                if file_txt != None:
                    shutil.move(file_txt, os.path.join(parent,'use_files',os.path.basename(file_txt))) 
            else:
                output_path = path_files
                for path, subdirs, files in os.walk(path_files):
                    for i,name in enumerate(files):
                        print("[" + str(i+1)+"/"+str(len(files))+"] Processando", name)
                        file_txt = self.__convert_to_txt(os.path.join(path, name))
                        if file_txt != None:
                            utils_module.create_folder(os.path.join(path_files,'use_files'))
                            shutil.move(file_txt, os.path.join(path_files,'use_files',os.path.basename(file_txt))) 

            df_result = self.__extract_information(registry,os.path.join(output_path,"use_files/**/*.txt"))
            date_now = datetime.now().strftime("%m%d%Y%H%M%S")
            if df_result is not None:
                df_result.to_excel(f"{PARENT_PATH}/resultado/processamento_{date_now}.xlsx", index=False)
                print("     Analise realizada com sucesso, resultado salvo em ",f"{PARENT_PATH}/resultado/processamento_{date_now}.xlsx")


        return None


if __name__ == "__main__":
    obj_extract = InfoExtract()
    if sys.argv[2] == "Y":
        utils_module.download_params(PARENT_PATH)
    obj_extract.extrair_dados(sys.argv[1], os.path.abspath(sys.argv[2]))