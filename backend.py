import streamlit as st
from langchain_community.utilities import sql_database

db = sql_database.SQLDatabase.from_uri("sqlite:///mdv.db")
import os

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
from langchain_experimental.sql import SQLDatabaseChain

cadena = SQLDatabaseChain.from_llm(llm, db, verbose=False)

formato = """
Dada una pregunta del usuario:
1. crea una consulta de sqlite3
2. revisa los resultados
3. devuelve el dato incluyendo siempre la url
4. si tienes que hacer alguna aclaración o devolver cualquier texto que sea siempre en español
{question}
"""


def consulta(input_usuario):
    consulta = formato.format(question=input_usuario)
    print("consulta: ", consulta)
    resultado = cadena.invoke(consulta)
    print("resultado: ", resultado)
    if resultado:
        return resultado["result"]
    # Imprimir el valor de 'result'
    return ""
