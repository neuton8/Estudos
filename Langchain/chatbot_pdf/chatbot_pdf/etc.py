from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import pathlib
from langchain_core.documents import Document
from uuid import uuid4

FILES_PATH = pathlib.Path(__file__).parents[0] / "files"

def load_files(files):
    output = []
    for file in files:
        loader = PyMuPDFLoader(file)
        for documento in loader.lazy_load():
            output.append(documento)

    return output


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)

def split_text(documentos):
    
    chunks = text_splitter.split_documents(documentos)

    for i,chunk in enumerate(chunks):
        chunks[i].metadata = {**chunks[i].metadata,"id":i}
    return chunks



def embed_and_load_db(chunks):
    embedder = HuggingFaceEmbeddings(model_name = 'sentence-transformers/all-MiniLM-L6-v2' )
    chroma_db = Chroma(collection_name="pdfs",embedding_function=embedder)
    uuids = [str(uuid4()) for _ in range(len(chunks))]
    chroma_db.add_documents(documents=chunks,ids=uuids)
    return chroma_db

def create_retriever(files):
    loaded_files = load_files(files)
    splitted_files = split_text(loaded_files)
    db = embed_and_load_db(splitted_files)
    return db.as_retriever(search_type="mmr", search_kwargs={"k": 5, "fetch_k": 20})

if __name__ == "__main__":
    files = FILES_PATH.glob("*.pdf")
    loaded_files = load_files(files)
    splitted_files = split_text(loaded_files)
    db = embed_and_load_db(splitted_files)
    print('test')
