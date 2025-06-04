from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator, model_validator
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

    @model_validator(mode="after")
    def validar_campos_obrigatorios(self) -> 'Frete':
        if self.peso_total_carga is None and self.quantidade_caminhoes is None:
            raise ValueError("Informe 'peso_total_carga' ou 'quantidade_caminhoes'.")
        if self.quantidade_caminhoes is not None and not self.tipo_rodado:
            raise ValueError("Se 'quantidade_caminhoes' for informado, 'tipo_rodado' também é obrigatório.")
        return self

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

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Erro do MySQL: {e.msg}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro geral: {str(e)}")
