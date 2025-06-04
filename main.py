from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, root_validator
from typing import Optional
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class Frete(BaseModel):
    origem: str
    destino: str
    valor_por_tonelada: float
    valor_diaria: float
    peso_total_carga: Optional[float] = None
    quantidade_caminhoes: Optional[int] = None
    tipo_rodado: Optional[str] = None
    precisa_engate: bool

    @root_validator()
    def check_required_fields(cls, values):
        peso = values.get("peso_total_carga")
        qtd = values.get("quantidade_caminhoes")
        tipo = values.get("tipo_rodado")

        if not peso and not qtd:
            raise ValueError("Você deve fornecer 'peso_total_carga' ou 'quantidade_caminhoes'.")
        if qtd and not tipo:
            raise ValueError("Se 'quantidade_caminhoes' for informado, 'tipo_rodado' também é obrigatório.")
        return values

@app.post("/adicionar-frete")
def adicionar_frete(frete: Frete):
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT"))
        )
        cursor = conn.cursor()

        query = """
        INSERT INTO fretes (
            origem, destino, valor_por_tonelada, valor_diaria,
            peso_total_carga, quantidade_caminhoes, tipo_rodado, precisa_engate
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        data = (
            frete.origem,
            frete.destino,
            frete.valor_por_tonelada,
            frete.valor_diaria,
            frete.peso_total_carga,
            frete.quantidade_caminhoes,
            frete.tipo_rodado,
            int(frete.precisa_engate)
        )

        cursor.execute(query, data)
        conn.commit()
        cursor.close()
        conn.close()

        return {"status": "sucesso", "mensagem": "Frete cadastrado com sucesso."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
