import streamlit as st
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from src.constants import FAISS_INDEX_PATH

load_dotenv()

st.set_page_config(page_title="RAG Chatbot", page_icon="🤖")
st.title("FAQ RAG Chatbot")

@st.cache_resource
def load_rag():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.load_local(
        FAISS_INDEX_PATH,
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


rag_chain, retriever = load_rag()

if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about a product...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            docs = retriever.invoke(user_input)
            answer = rag_chain.invoke(user_input)

            st.markdown(answer)

            with st.expander("📚 Sources"):
                for doc in docs[:3]:
                    st.write(f"**Product:** {doc.metadata.get('product')}")
                    st.write(doc.page_content[:200])
                    st.write("---")

    st.session_state.messages.append({"role": "assistant", "content": answer})