"""MÓDULO PARA PROCESSAMENTO DOS DADOS E EXTRAÇÃO DE INFORMAÇÕES"""
#%%
from glob import glob
import pandas as pd
import re
import sys
from ocr import transformFile
import os
from datetime import datetime
#%%
# colunas que constam da tabela com as expressões regulares
COLUMNS = ["lower_bound", "upper_bound", "group", "re.I", "multiple", "padrao"]
PARENT_PATH = os.path.dirname(os.path.dirname(sys.argv[0]))

#%%
def load_columns_table(
    name_table: str,
    excel_path: str = f"{PARENT_PATH}/docs/colunas_tabelas.xlsx",
):
    """
    Carrega os nomes das variáveis que serão inseridas na tabela respectiva.
    Caso não haja, para o cartório específico um padrão para captura da variável, este método garante o preenchimento com NDA.
    Ele também permite que além do método do cartório específico, sejam utilizados os padrões marcados com a tag 'geral'.
    """
    df = pd.read_excel(excel_path)
    return df["campo"][
        (df["nome_tabela"] == name_table) | ((df["nome_tabela"] == "geral"))
    ].tolist()

def load_data_excel(excel_path: str):
    "Lê uma tabela de excel simples"
    return pd.read_excel(excel_path)


def main_load(
    registry,
    excel_path: str = f"{PARENT_PATH}/docs/padroes_informações.xlsx",
    name_table: str = "informacoes_matriculas",
):
    "Carrega os padrões na forma de um dicionário para serem utilizados na extração de informações"
    df_patterns = load_data_excel(excel_path)
    df_name_variables = load_columns_table(name_table)
    df_patterns = df_patterns[df_patterns["cartorio"] == registry]
    dic_data = {}
    for row in df_patterns.to_dict("records"):
        dic_data[row["descrição"]] = {k: row[k] for k in COLUMNS}
    for k in df_name_variables:
        if k not in dic_data:
            dic_data[k] = "NDA"
    return dic_data

def extract_information(registry: str, path_files: str):
    """
    registry: nome do cartório cujos padrões serão utilizados, além de padrões com tag 'geral', se existirem
    path_files: caminho absoluto onde os arquivos podem ser encontrados

    Retorna um dataframe que pode ser transformado em um excel ou inserido na base de dados
    """
    dict_data = main_load(registry)
    list_files = glob(path_files, recursive=True)
    new_rows = []
    for f in list_files:
        print("Extracting information from ", f)
        text = re.sub(
            r"\s+", " ", " ".join([l for l in open(f, "r", encoding="utf-8")])
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

#%%
def main(registry: str, path_files: str):
    print(registry,path_files,PARENT_PATH)
    pdf_files = glob(f"{path_files}/*.pdf", recursive=True)
    for file in pdf_files:
        transformFile(file)
    
    return extract_information(registry,path_files + "/**/*.txt")


if __name__ == "__main__":
    df_result = main(sys.argv[1], sys.argv[2].replace("\\", "\/"))
    date_now = datetime.now().strftime("%m%d%Y%H%M%S")
    df_result.to_excel(f"{PARENT_PATH}/resultado/processamento_{date_now}.xlsx", index=False)
