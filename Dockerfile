# Etapa 1: imagem base com Python
FROM python:3.13-slim

# Diretório de trabalho no container
WORKDIR /app

# Copia arquivos para dentro da imagem
COPY . /app

# Instala dependências
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir fastapi uvicorn mysql-connector-python python-dotenv

# Expõe a porta usada pela aplicação
EXPOSE 6832

# Comando para rodar o servidor FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6832"]
