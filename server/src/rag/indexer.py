import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from memory.vector_store import vector_store
from utils.logging import logger


class Indexer:
    def __init__(self, config):
        self.config = config

    def index_documents(self, file_path):
        loader = PyPDFLoader(file_path)

        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True)
        
        all_splits = text_splitter.split_documents(docs)
        ids = vector_store.add_documents(documents=all_splits)

        return ids, file_path