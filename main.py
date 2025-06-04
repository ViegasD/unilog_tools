from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, model_validator
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
async def adicionar_frete(request: Request):
    try:
        body = await request.json()

        frete = Frete(
            origem=body.get("parameters0_Value"),
            destino=body.get("parameters1_Value"),
            valor_por_tonelada=float(body.get("parameters2_Value")),
            valor_diaria=float(body.get("parameters3_Value")),
            peso_total_carga=float(body.get("parameters4_Value")) if body.get("parameters4_Value") else None,
            quantidade_caminhoes=int(body.get("parameters5_Value")) if body.get("parameters5_Value") else None,
            tipo_rodado=body.get("parameters6_Value"),
            precisa_engate=bool(body.get("parameters7_Value"))
        )

        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT"))
        )
        cursor = conn.cursor()
                
        cursor.execute("USE unilog;")

        query = """
        INSERT INTO fretes (
            origem, destino, valor_por_tonelada, valor_diaria,
            peso_total_carga, quantidade_caminhoes, tipo_rodado, precisa_engate
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            frete.origem,
            frete.destino,
            frete.valor_por_tonelada,
            frete.valor_diaria,
            frete.peso_total_carga,
            frete.quantidade_caminhoes,
            frete.tipo_rodado,
            int(frete.precisa_engate)
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return {"status": "sucesso", "mensagem": "Frete cadastrado com sucesso."}

    except mysql.connector.Error as e:
        return {"status": "erro_mysql", "mensagem": f"{e.msg}"}

    except Exception as e:
        return {"status": "erro_geral", "mensagem": f"{str(e)}"}
