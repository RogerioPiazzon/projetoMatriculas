"""MÓDULO PARA CARREGAR DADOS"""

import pandas as pd
import os

from sqlalchemy import create_engine
from urllib.parse import quote_plus
from pathlib import Path

user = os.environ.get("USER")
pw = os.environ.get("PASS")
db = os.environ.get("DB")
host = os.environ.get("HOST")
api = os.environ.get("API")
port = os.environ.get("PORT")

# colunas que constam da tabela com as expressões regulares
COLUMNS = ["lower_bound", "upper_bound", "group", "re.I", "multiple", "padrao"]
QUERY_PADROES = " ".join(
    [l for l in open(Path().absolute().parent / "queries/padroes.sql")]
)
QUERY_VARIAVEIS = " ".join(
    [l for l in open(Path().absolute().parent / "queries/variaveis.sql")]
)


def load_columns_table(
    name_table: str,
    excel_path: str = "D:/Carlotti Consultoria/src/Projeto Matrículas/docs/colunas_tabelas.xlsx",
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


def load_data_db(query: str):
    "Se conecta na base de dados e executa alguma query específica"
    uri = (
        f"postgresql+psycopg2://{quote_plus(user)}:{quote_plus(pw)}@{host}:{port}/{db}"
    )
    alchemyEngine = create_engine(uri)
    dbConnection = alchemyEngine.connect()
    return pd.read_sql(query, dbConnection)


def load_data_excel(excel_path: str):
    "Lê uma tabela de excel simples"
    return pd.read_excel(excel_path)


def main_load(
    registry,
    excel_path: str = "D:/Carlotti Consultoria/src/Projeto Matrículas/docs/padroes_informações.xlsx",
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


def main_load_db(
    registry,
    name_table: str = "informacoes_matriculas",
):
    "Carrega os padrões na forma de um dicionário para serem utilizados na extração de informações"
    df_patterns = load_data_db(QUERY_PADROES.strip() + f" '{registry}'")
    df_name_variables = load_data_db(QUERY_VARIAVEIS.strip() + f" '{name_table}'")
    df_patterns = df_patterns[df_patterns["cartorio"] == registry]
    dic_data = {}
    for row in df_patterns.to_dict("records"):
        dic_data[row["descrição"]] = {k: row[k] for k in COLUMNS}
    for k in df_name_variables:
        if k not in dic_data:
            dic_data[k] = "NDA"
    return dic_data


def upload_data_db(df: pd.DataFrame, table_name: str = "matriculas"):
    uri = (
        f"postgresql+psycopg2://{quote_plus(user)}:{quote_plus(pw)}@{host}:{port}/{db}"
    )
    alchemyEngine = create_engine(uri)
    dbConnection = alchemyEngine.connect()
    df.to_sql(table_name, con=dbConnection, if_exists="append", index=False)


if __name__ == "__main__":
    print(load_columns_table("informacoes_matriculas"))
