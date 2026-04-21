import pandas as pd
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv
import os 
import sys
import time
from pathlib import Path


from src.exception.exception import ChatBotException
from src.logging.logger import logging
from src.constants import INPUT_FILE_PATH, FAQ_OUTPUT_PATH


def make_prompt(product_name: str , reviews: str) -> str:
    prompt=f"""You are a helpful customer assistant.
    Based on the real customer reviews of {product_name},generate 3 to 5 frequently asked question and their answers.
    keep the answers conise helpful and grounded in review .
    Reviews:
    {reviews}
    Format strictly as :
    Q1: ....
    A1: ...
    Q2: ...
    A2: ...
    """
    return prompt

def generate_faqs(input_path: Path = INPUT_FILE_PATH, output_path: Path = FAQ_OUTPUT_PATH):
    logging.info("Starting the FAQ generation process")
    load_dotenv()
    logging.info("Configuring the Groq API")
    api_key=os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in the environment variables")
    
    client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

    logging.info("Reading the dataset")
    df=pd.read_excel(input_path)
    df=df[['name','reviews.text']].dropna()
    df = df.groupby('name')['reviews.text'].apply(lambda x: ' '.join(x[:25])).reset_index()

    faq_data=[]

    for _,row in tqdm(df.iterrows(),total=len(df)):
        product=row["name"]
        reviews=row["reviews.text"]
        prompt=make_prompt(product,reviews)
        try:
            response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7
                        )

            faqs = response.choices[0].message.content
            faq_data.append({'product_name': product, 'faqs': faqs})
            time.sleep(5)
        except Exception as e:
            raise ChatBotException(e,sys)
        
    pd.DataFrame(faq_data).to_csv(FAQ_OUTPUT_PATH,index=False)
    logging.info(f"FAQS SAVED TO {output_path}")
    logging.info("FAQS generation completed successfully")

if __name__=="__main__":
    generate_faqs()

