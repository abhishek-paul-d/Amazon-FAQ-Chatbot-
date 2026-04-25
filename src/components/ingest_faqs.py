import os
import sys
from pathlib import Path
import pandas as pd

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from src.exception.exception import ChatBotException
from src.logging.logger import logging
from src.constants import FAQ_OUTPUT_PATH, FAISS_INDEX_PATH


def ingest_faqs(
    faq_path: Path = FAQ_OUTPUT_PATH,
    index_path: Path = FAISS_INDEX_PATH
):
    try:
        logging.info("Starting FAQ Ingestion process")
        logging.info(f"Reading FAQ file from {faq_path}")
        if not os.path.exists(faq_path):
            raise FileNotFoundError(f"File not found: {faq_path}")

        df = pd.read_csv(faq_path)

        required_cols = ['product_name', 'faqs']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        df = df.dropna()

        logging.info("Converting FAQs into LangChain Documents")

        documents = []
        for _, row in df.iterrows():
            doc = Document(
                page_content=row["faqs"],
                metadata={"product": row["product_name"]}
            )
            documents.append(doc)

        logging.info("Splitting documents into chunks")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        split_docs = splitter.split_documents(documents)

        logging.info(f"Total chunks created: {len(split_docs)}")

        logging.info("Creating embeddings using Hugging Face MiniLM")

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},   # change to "cuda" if GPU available
            encode_kwargs={"normalize_embeddings": True}
        )

        logging.info("Creating FAISS index")
        vector_store = FAISS.from_documents(split_docs, embeddings)

        os.makedirs(index_path, exist_ok=True)
        vector_store.save_local(index_path)

        logging.info(f"FAISS index saved at {index_path}")
        logging.info("FAQ ingestion completed successfully")

    except Exception as e:
        logging.error(f"Error during FAQ ingestion: {str(e)}")
        raise ChatBotException(e, sys)

if __name__ == "__main__":
    ingest_faqs()