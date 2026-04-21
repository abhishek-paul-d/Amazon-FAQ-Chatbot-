import os 
from pathlib import Path

BASE_DIR = os.getcwd()

DATA_DIR = os.path.join(BASE_DIR,"data")

INPUT_FILE_PATH: Path = os.path.join(DATA_DIR,"amazon_reviews.xlsx")
FAQ_OUTPUT_PATH: Path = os.path.join(DATA_DIR,"generated_faqs_groq.csv")

FAISS_INDEX_PATH: Path = os.path.join(BASE_DIR,"faiss_index")

