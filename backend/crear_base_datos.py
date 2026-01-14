import os
import requests
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import FAISS

# 1. Cargar claves de seguridad
load_dotenv()

def descargar_biblia():
    if not os.path.exists("biblia.txt"):
        print("⬇️ Descargando Biblia Reina Valera (1909)...")
        url = "https://www.gutenberg.org/cache/epub/14976/pg14976.txt"
        response = requests.get(url)
        with open("biblia.txt", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("✅ Descarga lista.")
    return "biblia.txt"

def crear_base_datos():
    print("🚀 INICIANDO PROCESO ETL (Extracción, Transformación y Carga)...")
    
    # PASO A: Cargar Documento
    archivo = descargar_biblia()
    loader = TextLoader(archivo, encoding="utf-8")
    docs_raw = loader.load()
    print("📚 Biblia cargada en memoria.")

    # PASO B: Definir Embeddings (El cerebro semántico)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    # PASO C: Chunking Semántico (La técnica del video)
    # Cortamos por significado, no por caracteres.
    print("⚡ Aplicando Semantic Chunking (esto tardará unos minutos)...")
    text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type="percentile")
    chunks = text_splitter.split_documents(docs_raw)
    print(f"🧩 Se crearon {len(chunks)} fragmentos semánticos.")

    # PASO D: Crear y Guardar Vector Store (FAISS)
    print("💾 Guardando base de datos vectorial en disco local...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # Esto crea una carpeta "faiss_index" que persiste en tu Codespace
    vectorstore.save_local("faiss_index") 
    print("✅ ¡ÉXITO! Base de datos 'faiss_index' creada.")

if __name__ == "__main__":
    crear_base_datos()
