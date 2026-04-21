import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.logging.logger import logging
from src.components.generate_faqs import generate_faqs
from src.exception.exception import ChatBotException
if __name__ == "__main__":
    try:
        generate_faqs()
    except Exception as e:
        raise ChatBotException(e,sys)

