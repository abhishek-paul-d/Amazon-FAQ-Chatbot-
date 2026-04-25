import sys
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from langchain_core.messages import HumanMessage, AIMessage

from src.logging.logger import logging
from src.constants import FAISS_INDEX_PATH


def load_rag_pipeline(index_path: Path = FAISS_INDEX_PATH):
    load_dotenv()

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.load_local(
        index_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    llm = ChatOllama(model="llama3", temperature=0.4)

    prompt = ChatPromptTemplate.from_template(
        """You are a helpful assistant.

Use ONLY the context below to answer the question.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question:
{question}
"""
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever


if __name__ == "__main__":
    try:
        rag_chain, retriever = load_rag_pipeline()
        chat_history = []

        print("\nRAG Chatbot Ready\n")

        while True:
            query = input("You: ")

            if query.lower() in ["exit", "quit"]:
                break

            docs = retriever.invoke(query)
            answer = rag_chain.invoke(query)

            print("\nBot:", answer)

            print("\nSources:")
            for doc in docs[:2]:
                print("-", doc.metadata.get("product"), ":", doc.page_content[:100])

            chat_history.append(HumanMessage(content=query))
            chat_history.append(AIMessage(content=answer))

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise Exception(str(e))