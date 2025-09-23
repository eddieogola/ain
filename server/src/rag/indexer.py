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

    def search(self, query):
        # Logic to search indexed documents
        results = vector_store.similarity_search(
            query, k=3
        )

        retrieved_context = list(map(lambda result: result.page_content, results))
        combined_context = "\n\n".join(retrieved_context)

        return combined_context
