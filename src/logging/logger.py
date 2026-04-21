import logging 
from datetime import datetime
import os 
import sys

LOG_FILE=f"{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.log"

logs_path=os.path.join(os.getcwd(),"logs",LOG_FILE)
os.makedirs(os.path.dirname(logs_path), exist_ok=True)

LOG_FILE_PATH = logs_path

logging.basicConfig(
    filename = LOG_FILE_PATH,
    format = "[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
    level = logging.INFO
)