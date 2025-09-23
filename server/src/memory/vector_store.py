from langchain_chroma import Chroma
from config import get_config

config = get_config()
embeddings = config.embed_model

vector_store = Chroma(
    collection_name="ain_docs_v1",
    embedding_function=embeddings,
    persist_directory=config.vector_store_dir,  # Where to save data locally, remove if not necessary
)