"Servidor fast API com exposição de um método para transformação de arquivos"

from fastapi import (
    FastAPI,
    Request,
)
from pydantic import BaseModel

from information_extraction import main

OUTPUT_PATH = "C:/Users/danil/Desktop/test_matriculas.xlsx"

app = FastAPI()


class Data(BaseModel):
    registry: str
    path_files: str


@app.post("/process_files")
def index(request: Request, data: Data):
    data = data.dict()
    df_result = main(
        data["registry"], data["path_files"].replace("\\", "\/") + "/**/*.txt"
    )
    df_result.to_excel(OUTPUT_PATH, index=False)
