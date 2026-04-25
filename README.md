# 🤖 RAG Product FAQ Chatbot

> **Retrieval-Augmented Generation system that transforms raw product reviews into an intelligent, conversational FAQ engine — with both CLI and web interfaces.**

---

## 📸 Quick Demo

![FAQ RAG Chatbot Web UI](<img width="1920" height="1080" alt="Screenshot 2026-04-25 182506" src="https://github.com/user-attachments/assets/581d960c-57ec-4bc4-b7e4-d417e0487cb8" />
)
<img width="1920" height="1080" alt="Screenshot 2026-04-25 182543" src="https://github.com/user-attachments/assets/298a6f0c-cdca-4e4b-aa57-aa2fb1ea3f7c" />

The web UI (running at `localhost:8501`) answers a natural-language product question and expands a **Sources** panel showing the exact FAQ chunks retrieved — including the originating product name and the Q&A text used to construct the answer.

---

## 🏗️ Architecture

```
                     ┌──────────────────────────────────────────────┐
                     │             DATA PIPELINE (offline)          │
                     │                                              │
  Excel Reviews      │  generate_faqs.py       ingest_faqs.py      │
  (.xlsx)  ──────────►  [Groq / Llama 3.1] ──► [Embeddings +       │
                     │   ↓                      FAISS Index]        │
                     │   product_faqs.csv   ──► faiss_index/        │
                     └──────────────────────────────────────────────┘
                                                    │
                                        ┌───────────▼────────────┐
                                        │    RETRIEVAL ENGINE    │
                                        │  all-MiniLM-L6-v2      │
                                        │  FAISS top-k=4         │
                                        └───────────┬────────────┘
                                                    │
                              ┌─────────────────────▼─────────────────────┐
                              │          INFERENCE LAYER (online)          │
                              │  Ollama Llama 3 (local)                    │
                              │  + Retrieved context + Chat history         │
                              │  + Source attribution                       │
                              └──────────────┬──────────────────────────────┘
                                             │
                           ┌─────────────────▼──────────────────┐
                           │           USER INTERFACES           │
                           │  rag_chatbot.py   streamlit_app.py  │
                           │      (CLI)            (Web UI)      │
                           └─────────────────────────────────────┘
```

**Data flows in two phases:**

1. **Offline pipeline** (`generate_faqs.py` → `ingest_faqs.py`): run once to process reviews into a persistent vector index.
2. **Online inference** (`rag_chatbot.py` / `streamlit_app.py`): loads the index and serves queries in real time with no API calls required.

---

## 🛠️ Tech Stack

| Component | Technology | Rationale |
|---|---|---|
| **FAQ Generation LLM** | Groq API (Llama 3.1) | Groq's LPU inference runs at ~500 tok/s — ideal for the one-time, batch generation pass where speed matters. |
| **Inference LLM** | Ollama (Llama 3, local) | Zero cost per query, no data egress, sub-second first-token latency for interactive sessions. |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | 384-dim vectors; 5× faster than `text-embedding-ada-002`, no API dependency, strong semantic recall on Q&A text. |
| **Vector Store** | FAISS (`IndexFlatL2`) | In-process, no server to manage. Exact search is sufficient at FAQ scale; no quantization tradeoffs needed. |
| **Orchestration** | LangChain | `RecursiveCharacterTextSplitter` and `FAISS` integrations reduce boilerplate without hiding the RAG logic. |
| **Web UI** | Streamlit | `@st.cache_resource` keeps the model loaded across re-renders; `session_state` handles multi-turn history. |
| **Data I/O** | pandas (Excel → CSV) | Handles multi-sheet `.xlsx` with mixed dtypes; `groupby` makes per-product batching clean and readable. |

---

## 📁 Folder Structure

```
FAQ_CHATBOT/
│
├── src/
│   ├── components/
│   │   ├── __init__.py
│   │   ├── generate_faqs.py    # Stage 1 — Reviews → FAQ CSV via Groq/Llama 3.1
│   │   ├── ingest_faqs.py      # Stage 2 — FAQ CSV → FAISS vector index
│   │   └── rag_chatbot.py      # Core RAG retrieval + response logic
│   ├── constants/              # App-wide constants (paths, model names, etc.)
│   ├── exception/              # Custom RAGException hierarchy
│   ├── logging/                # Logging configuration
│   └── __init__.py
│
├── data/
│   ├── amazon_reviews.xlsx     # Input: raw product reviews
│   └── generated_faqs_groq.csv # Generated: structured Q&A pairs
│
├── faiss_index/                # Generated: persisted vector store
│
├── logs/
│   └── 25-04-2026_17-32-25.log # Timestamped run logs
│
├── app.py                      # Streamlit web UI entry point
├── main.py                     # CLI entry point
├── pyproject.toml
├── requirements.txt
├── uv.lock
├── .env
├── .gitignore
├── .python-version
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.ai) installed and running locally
- A [Groq API key](https://console.groq.com)

```bash
# Pull the local inference model (one-time, ~4 GB)
ollama pull llama3
```

### 1. Clone & Install

```bash
git clone https://github.com/your-username/rag-faq-chatbot.git
cd rag-faq-chatbot

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
# Required
GROQ_API_KEY=gsk_...

# Paths
REVIEWS_FILE=data/reviews.xlsx
FAQS_OUTPUT=output/product_faqs.csv
FAISS_INDEX_PATH=faiss_index

# RAG hyperparameters (tune without touching code)
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=4
REVIEWS_PER_PRODUCT=25
```

### 3. Run the Data Pipeline

```bash
# Stage 1: Generate FAQs from reviews
#   Reads reviews.xlsx, groups by product, calls Groq API
#   Output: output/product_faqs.csv
python generate_faqs.py

# Stage 2: Build the vector index
#   Loads CSV, chunks text, creates embeddings, saves FAISS index
#   Runtime: ~30s for 1,000 FAQ entries on CPU
python ingest_faqs.py
```

### 4. Launch the Chatbot

streamlit run streamlit_app.py
# Opens at http://localhost:8501
```
---

## 💬 Sample Interaction

```
$ python rag_chatbot.py

Loading FAISS index from faiss_index/... ✓
Connecting to Ollama (llama3)... ✓
Ready. Type 'quit' to exit, 'clear' to reset chat history.
──────────────────────────────────────────────────────────

You: can i access Google Play store in Fire HD 8
Assistant: Based on the context, I can answer your question:

  Yes, you can access Google Play Store on the Fire HD 8 Tablet.
  (Refer to A4: Yes, although it requires some technical know-how,
  some reviewers have successfully installed the Google Play Store
  on the tablet.)

▼ Sources
  ┌─────────────────────────────────────────────────────────────────┐
  │ Product: Fire Tablet with Alexa, 7 Display, 16 GB, Blue        │
  │ Q2: Can I access Google apps on the Fire Tablet?               │
  │ A2: Unfortunately, no. Many reviewers have mentioned that the  │
  │ tablet can only access Amazon apps, and not Google Play Store. │
  │ However, some reviewers ha[ve found workarounds]...            │
  ├─────────────────────────────────────────────────────────────────┤
  │ Product: All-New Fire HD 8 Tablet, 8 HD Display, Wi-Fi, 16 GB │
  │ Q4: Can I access Google Play Store on the Fire HD 8 Tablet?   │
  │ A4: Yes, although it requires some technical know-how, some   │
  │ reviewers have successfully installed the Google Play Store.  │
  ├─────────────────────────────────────────────────────────────────┤
  │ Product: Fire Tablet, 7 Display, Wi-Fi, 16 GB, Black          │
  │ Q1: Is the Fire Tablet compatible with other devices, such as │
  │ Google Cast? A1: No, the Fire Tablet is not compatible wit... │
  └─────────────────────────────────────────────────────────────────┘
```

---

*Built with Python 3.11 · LangChain 0.2 · FAISS · Streamlit 1.35 · Ollama · Groq API*
