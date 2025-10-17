import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from src.llm_init import init_langchain_embedding
import docx


def build_vectorstores(file_path, chunk_size, chunk_overlap, output_path, spliter=''):

    if file_path.endswith('.docx'):
        data = get_content_docx(file_path)
    model = init_langchain_embedding()
    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    if len(spliter) > 0:
        vector_stores = data.split(spliter)
    else:
        vector_stores = text_splitter.split_text(data)
    metadata = [{"source": f'[{file_path}].{i} '} for i in range(len(vector_stores))]
    db = Chroma.from_texts(vector_stores, model, metadatas=metadata,  persist_directory=output_path)
    db.persist()
    print(f'Encoded and saved to {output_path}')


def get_content_docx(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)


def get_similar_text(query, vectordb_path, k=10):
    model = init_langchain_embedding()
    db = Chroma(
        persist_directory=vectordb_path,
        embedding_function=model)
    docs = db.similarity_search(query, k=k)
    return docs

